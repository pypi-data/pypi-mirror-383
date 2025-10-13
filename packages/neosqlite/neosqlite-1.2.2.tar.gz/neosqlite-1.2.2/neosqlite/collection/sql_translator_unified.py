"""
Unified SQL translation framework for NeoSQLite.

This module provides a unified approach to translating MongoDB-style queries
into SQL statements that can be used both for direct execution and for
temporary table generation.
"""

from .cursor import DESCENDING
from .jsonb_support import should_use_json_functions
from typing import Any, Dict, List, Tuple


def _empty_result() -> Tuple[str, List[Any]]:
    """
    Return an empty result tuple for fallback cases.

    Returns:
        Tuple[str, List[Any]]: A tuple containing an empty string and an empty list.
    """
    return "", []


def _text_search_fallback() -> Tuple[None, List[Any]]:
    """
    Return a text search result tuple for fallback cases.

    Returns:
        Tuple[None, List[Any]]: A tuple containing None and an empty list.
    """
    return None, []


class SQLFieldAccessor:
    """
    Handles field access patterns for different contexts.

    This class provides methods to generate appropriate SQL expressions
    for accessing fields in different contexts, such as direct table access
    or temporary table access.
    """

    def __init__(
        self,
        data_column: str = "data",
        id_column: str = "id",
        jsonb_supported: bool = False,
    ):
        """
        Initialize the SQLFieldAccessor with column names.

        Args:
            data_column: The name of the column containing JSON data (default: "data")
            id_column: The name of the column containing document IDs (default: "id")
            jsonb_supported: Whether JSONB functions are supported (default: False)
        """
        self.data_column = data_column
        self.id_column = id_column
        self.jsonb_supported = jsonb_supported

    def _parse_json_path(self, field: str) -> str:
        """
        Convert dot notation with array indexing to JSON path syntax.

        Supports:
        - Simple fields: "name" -> "$.name"
        - Nested fields: "address.street" -> "$.address.street"
        - Array indexing: "tags[0]" -> "$.tags[0]"
        - Nested array access: "orders.items[2].name" -> "$.orders.items[2].name"
        - Complex paths: "a.b[0].c[1].d" -> "$.a.b[0].c[1].d"

        Args:
            field (str): The field path in dot notation with optional array indices

        Returns:
            str: Properly formatted JSON path
        """

        # Handle special case for _id
        if field == "_id":
            return field

        # Pattern to match field names with optional array indices
        # This pattern matches sequences like "field", "field[0]", "field[0][1]", etc.

        # Split the field path by dots while preserving array indices
        parts = []
        current_part = ""

        i = 0
        while i < len(field):
            if field[i] == ".":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            elif field[i] == "[":
                # Find the closing bracket
                bracket_end = field.find("]", i)
                if bracket_end != -1:
                    # Add the array index to current part
                    current_part += field[i : bracket_end + 1]
                    i = bracket_end
                else:
                    # Malformed array index, treat as regular character
                    current_part += field[i]
            else:
                current_part += field[i]
            i += 1

        # Add the last part
        if current_part:
            parts.append(current_part)

        # Convert each part to JSON path format
        json_parts = []
        for part in parts:
            # Check if part contains array indices
            if "[" in part:
                # Split field name from array indices
                field_name_end = part.find("[")
                field_name = part[:field_name_end]
                array_indices = part[field_name_end:]
                json_parts.append(f"{field_name}{array_indices}")
            else:
                json_parts.append(part)

        return f"$.{'.'.join(json_parts)}"

    def get_field_access(
        self, field: str, context: str = "direct", query: dict | None = None
    ) -> str:
        """
        Generate field access SQL with enhanced JSON path support.

        This method generates appropriate SQL expressions for accessing fields
        based on the field name and context. For the special "_id" field, it returns
        the _id column name for direct access. For other fields, it generates a
        json_extract or jsonb_extract expression to access the field from the JSON
        data column, with support for complex JSON paths including array indexing.

        Args:
            field: The field name to access
            context: The context for field access (default: "direct")
            query: The query being processed (used to determine if text search is needed)

        Returns:
            SQL expression for accessing the field
        """
        if field == "_id":
            # Special handling for _id field - access the _id column directly
            return "_id"
        else:
            # Use enhanced JSON path parsing
            json_path = self._parse_json_path(field)

            # Determine whether to use json_* or jsonb_* functions
            use_json = should_use_json_functions(query, self.jsonb_supported)
            function_name = "json_extract" if use_json else "jsonb_extract"

            return f"{function_name}({self.data_column}, '{json_path}')"


class SQLOperatorTranslator:
    """
    Translates MongoDB operators to SQL expressions.

    This class handles the translation of MongoDB query operators (like $eq, $gt, $in, etc.)
    into equivalent SQL expressions. It uses an SQLFieldAccessor to generate appropriate
    field access expressions for different contexts.
    """

    def __init__(self, field_accessor: SQLFieldAccessor | None = None):
        """
        Initialize the SQLOperatorTranslator with an optional field accessor.

        Args:
            field_accessor: An SQLFieldAccessor instance to use for field access expressions.
                            If None, a default SQLFieldAccessor will be created.
        """
        self.field_accessor = field_accessor or SQLFieldAccessor()

    def translate_operator(
        self, field_access: str, operator: str, value: Any
    ) -> Tuple[str | None, List[Any]]:
        """
        Translate a MongoDB operator to SQL.

        This method handles the translation of MongoDB query operators into equivalent
        SQL expressions. It supports various operators including comparison operators
        ($eq, $gt, $lt, $gte, $lte, $ne), array operators ($in, $nin), existence checks
        ($exists), modulo operations ($mod), array size checks ($size), and substring
        searches ($contains).

        Special handling is included for Binary objects which are serialized using
        the compact format for SQL comparisons.

        Args:
            field_access: The SQL expression for accessing the field
            operator: The MongoDB operator ($eq, $gt, etc.)
            value: The value to compare against

        Returns:
            Tuple of (SQL expression, parameters) or (None, []) if unsupported
        """
        # default `sql` and `params`
        sql: str | None = None
        params: List[Any] = []

        # Serialize Binary objects for SQL comparisons using compact format
        if isinstance(value, bytes) and hasattr(value, "encode_for_storage"):
            from .json_helpers import neosqlite_json_dumps_for_sql

            value = neosqlite_json_dumps_for_sql(value)

        # Check if this is a datetime comparison that should be wrapped with datetime() function
        # This is needed when datetime fields are indexed using datetime(json_extract(...)) for timezone normalization
        is_datetime_comparison = (
            operator in ("$eq", "$gt", "$lt", "$gte", "$lte", "$ne")
            and isinstance(value, str)
            and self._is_datetime_value(value)
        ) or (
            operator in ("$in", "$nin")
            and isinstance(value, (list, tuple))
            and len(value) > 0  # Only if there are elements to check
            and all(
                isinstance(v, str) and self._is_datetime_value(v) for v in value
            )
        )

        # If it's a datetime comparison, wrap both field and value with datetime() to match indexing strategy
        if is_datetime_comparison:
            # Wrap the field access with datetime() function for consistency with datetime indexes
            datetime_field_access = f"datetime({field_access})"
            match operator:
                case "$eq":
                    sql = f"{datetime_field_access} = datetime(?)"
                    params = [value]
                case "$gt":
                    sql = f"{datetime_field_access} > datetime(?)"
                    params = [value]
                case "$lt":
                    sql = f"{datetime_field_access} < datetime(?)"
                    params = [value]
                case "$gte":
                    sql = f"{datetime_field_access} >= datetime(?)"
                    params = [value]
                case "$lte":
                    sql = f"{datetime_field_access} <= datetime(?)"
                    params = [value]
                case "$ne":
                    sql = f"{datetime_field_access} != datetime(?)"
                    params = [value]
                case "$in":
                    if isinstance(value, (list, tuple)):
                        placeholders = ", ".join("datetime(?)" for _ in value)
                        sql = f"{datetime_field_access} IN ({placeholders})"
                        params = list(value)
                case "$nin":
                    if isinstance(value, (list, tuple)):
                        placeholders = ", ".join("datetime(?)" for _ in value)
                        sql = f"{datetime_field_access} NOT IN ({placeholders})"
                        params = list(value)
                case _:
                    # For unsupported operators with datetime values, fall back to regular processing
                    is_datetime_comparison = False
                    # Use regular processing below
        else:
            # Regular processing for non-datetime values
            match operator:
                case "$eq":
                    sql = f"{field_access} = ?"
                    params = [value]
                case "$gt":
                    sql = f"{field_access} > ?"
                    params = [value]
                case "$lt":
                    sql = f"{field_access} < ?"
                    params = [value]
                case "$gte":
                    sql = f"{field_access} >= ?"
                    params = [value]
                case "$lte":
                    sql = f"{field_access} <= ?"
                    params = [value]
                case "$ne":
                    sql = f"{field_access} != ?"
                    params = [value]
                case "$in":
                    if isinstance(value, (list, tuple)):
                        # For $in operator, check if all values are datetime to decide whether to use datetime() wrapper
                        # Only consider it as datetime if there are values AND all values are datetime strings
                        if len(value) > 0 and all(
                            isinstance(v, str) and self._is_datetime_value(v)
                            for v in value
                        ):
                            placeholders = ", ".join(
                                "datetime(?)" for _ in value
                            )
                            sql = (
                                f"datetime({field_access}) IN ({placeholders})"
                            )
                            params = list(value)
                        else:
                            placeholders = ", ".join("?" for _ in value)
                            sql = f"{field_access} IN ({placeholders})"
                            params = list(value)
                case "$nin":
                    if isinstance(value, (list, tuple)):
                        # For $nin operator, check if all values are datetime to decide whether to use datetime() wrapper
                        # Only consider it as datetime if there are values AND all values are datetime strings
                        if len(value) > 0 and all(
                            isinstance(v, str) and self._is_datetime_value(v)
                            for v in value
                        ):
                            placeholders = ", ".join(
                                "datetime(?)" for _ in value
                            )
                            sql = f"datetime({field_access}) NOT IN ({placeholders})"
                            params = list(value)
                        else:
                            placeholders = ", ".join("?" for _ in value)
                            sql = f"{field_access} NOT IN ({placeholders})"
                            params = list(value)
                case "$exists":
                    # Handle boolean value for $exists
                    if value is True:
                        sql = f"{field_access} IS NOT NULL"
                        params = []
                    elif value is False:
                        sql = f"{field_access} IS NULL"
                        params = []
                case "$mod":
                    # Handle [divisor, remainder] array
                    if isinstance(value, (list, tuple)) and len(value) == 2:
                        divisor, remainder = value
                        sql = f"{field_access} % ? = ?"
                        params = [divisor, remainder]
                case "$size":
                    # Handle array size comparison
                    if isinstance(value, int):
                        sql = f"json_array_length({field_access}) = ?"
                        params = [value]
                case "$contains":
                    # Handle case-insensitive substring search
                    # Convert value to string to match Python implementation behavior
                    str_value = str(value)
                    sql = f"lower({field_access}) LIKE ?"
                    params = [f"%{str_value.lower()}%"]
                case _:
                    # Unsupported operator
                    pass

        return sql, params

    def _is_datetime_value(self, value: Any) -> bool:
        """
        Check if a value is a datetime string.

        Args:
            value: Value to check

        Returns:
            True if value is a datetime string, False otherwise
        """
        from .datetime_utils import is_datetime_value

        return is_datetime_value(value)


class SQLClauseBuilder:
    """
    Builds SQL clauses with reusable components.

    This class provides methods to build various SQL clauses including WHERE, ORDER BY,
    and LIMIT/OFFSET clauses. It uses SQLFieldAccessor for field access and
    SQLOperatorTranslator for operator translations to create SQL expressions from
    MongoDB-style query specifications.
    """

    def __init__(
        self,
        field_accessor: SQLFieldAccessor | None = None,
        operator_translator: SQLOperatorTranslator | None = None,
    ):
        """
        Initialize the SQLClauseBuilder with optional field accessor and operator translator.

        Args:
            field_accessor: An SQLFieldAccessor instance to use for field access expressions.
                            If None, a default SQLFieldAccessor will be created.
            operator_translator: An SQLOperatorTranslator instance to use for operator translations.
                                 If None, a default SQLOperatorTranslator will be created.
        """
        self.field_accessor = field_accessor or SQLFieldAccessor()
        self.operator_translator = (
            operator_translator or SQLOperatorTranslator()
        )

    def _build_logical_condition(
        self,
        operator: str,
        conditions: List[Dict[str, Any]],
        context: str = "direct",
    ) -> Tuple[str | None, List[Any]]:
        """
        Build a logical condition ($and, $or, $nor, $not).

        This method handles the construction of SQL expressions for MongoDB logical operators.
        It recursively processes nested conditions and builds appropriate SQL expressions
        with proper parentheses grouping.

        Args:
            operator: The logical operator ($and, $or, $nor)
            conditions: List of condition dictionaries
            context: The context for field access (default: "direct")

        Returns:
            Tuple of (SQL expression, parameters) or (None, []) if unsupported
        """
        # default `sql` and `params`
        sql: str | None = None
        params: List[Any] = []

        if not isinstance(conditions, list):
            return sql, params

        clauses: List[str] = []

        for condition in conditions:
            if isinstance(condition, dict):
                # Recursively build condition
                clause, clause_params = self.build_where_clause(
                    condition, context, is_nested=True
                )
                if clause is None:
                    # Break and return the clauses built so far
                    break
                elif clause:  # Only add non-empty clauses
                    # Remove "WHERE " prefix if present
                    if clause.startswith("WHERE "):
                        clause = clause[6:]
                    clauses.append(f"({clause})")
                    params.extend(clause_params)
            else:
                break

        if not clauses:
            return _empty_result()

        match operator:
            case "$and":
                sql = " AND ".join(clauses)
            case "$or":
                sql = " OR ".join(clauses)
            case "$nor":
                sql = "NOT (" + " OR ".join(clauses) + ")"
            case _:
                # Unsupported logical operator
                pass

        return sql, params

    def build_where_clause(
        self,
        query: Dict[str, Any],
        context: str = "direct",
        is_nested: bool = False,
        query_param: dict | None = None,
    ) -> Tuple[str | None, List[Any]]:
        """
        Build a WHERE clause from a MongoDB-style query.

        This method translates a MongoDB-style query specification into an SQL WHERE clause.
        It handles both simple field conditions and complex logical operators ($and, $or, $nor, $not).
        The method recursively processes nested conditions and properly groups them with parentheses.

        Args:
            query: The MongoDB-style query
            context: The context for field access (default: "direct")
            is_nested: Whether this is a nested condition within a logical operator (default: False)
            query_param: The original query being processed (used to determine if text search is needed)

        Returns:
            Tuple of (WHERE clause, parameters) or (None, []) if unsupported
        """
        # default `sql` and `params`
        sql: str | None = None
        params: List[Any] = []
        # default `clauses`
        clauses: List[str] = []

        for field, value in query.items():
            if field in ("$and", "$or", "$nor"):
                # Handle logical operators directly
                sql, clause_params = self._build_logical_condition(
                    field, value, context
                )
                if sql is None:
                    return None, []  # Unsupported condition, fallback to Python
                else:  # Only add if not empty
                    clauses.append(sql)
                    params.extend(clause_params)
            elif field == "$not":
                # Handle $not logical operator (applies to single condition)
                if isinstance(value, dict):
                    not_clause, not_params = self.build_where_clause(
                        value, context, is_nested=True, query_param=query_param
                    )
                    if not_clause is None:
                        return (
                            None,
                            [],
                        )  # Unsupported condition, fallback to Python
                    if not_clause:
                        # Remove "WHERE " prefix if present
                        if not_clause.startswith("WHERE "):
                            not_clause = not_clause[6:]
                        clauses.append(f"NOT ({not_clause})")
                        params.extend(not_params)
                    else:
                        return _empty_result()  # Empty condition
                else:
                    return _empty_result()  # Invalid format for $not
            else:
                # Regular field condition
                # Get field access expression
                field_access = self.field_accessor.get_field_access(
                    field, context, query_param
                )

                if isinstance(value, dict):
                    # Handle query operators like $eq, $gt, $lt, etc.
                    for operator, op_val in value.items():
                        sql, clause_params = (
                            self.operator_translator.translate_operator(
                                field_access, operator, op_val
                            )
                        )
                        if sql is None:
                            # Unsupported operator, fallback to Python
                            return None, []
                        clauses.append(sql)
                        params.extend(clause_params)
                else:
                    # Simple equality check
                    clauses.append(f"{field_access} = ?")
                    params.append(value)

        if not clauses:
            return _empty_result()

        # Build the final WHERE clause
        where_clause = "WHERE " + " AND ".join(clauses)
        if is_nested:
            # Remove "WHERE " prefix for nested conditions
            where_clause = where_clause[6:]

        return where_clause, params

    def build_order_by_clause(
        self, sort_spec: Dict[str, Any], context: str = "direct"
    ) -> str:
        """
        Build an ORDER BY clause from a sort specification.

        This method translates a MongoDB-style sort specification into an SQL ORDER BY clause.
        It handles multiple sort fields with their respective sort directions (ascending or descending).

        Args:
            sort_spec: The sort specification mapping field names to sort directions
            context: The context for field access (default: "direct")

        Returns:
            ORDER BY clause as a string
        """
        if not sort_spec:
            return ""

        order_parts = []
        for field, direction in sort_spec.items():
            field_access = self.field_accessor.get_field_access(field, context)
            order_parts.append(
                f"{field_access} {'DESC' if direction == DESCENDING else 'ASC'}"
            )

        return "ORDER BY " + ", ".join(order_parts)

    def build_limit_offset_clause(
        self, limit_value: int | None = None, skip_value: int = 0
    ) -> str:
        """
        Build LIMIT and OFFSET clauses.

        This method constructs SQL LIMIT and OFFSET clauses based on the provided limit and skip values.
        It handles the special case where SQLite requires a LIMIT clause when using OFFSET.

        Args:
            limit_value: The limit value (default: None)
            skip_value: The skip value (default: 0)

        Returns:
            LIMIT and OFFSET clauses as a string
        """
        limit_clause = ""
        if limit_value is not None:
            if skip_value > 0:
                limit_clause = f"LIMIT {limit_value} OFFSET {skip_value}"
            else:
                limit_clause = f"LIMIT {limit_value}"
        elif skip_value > 0:
            # SQLite requires LIMIT when using OFFSET
            limit_clause = f"LIMIT -1 OFFSET {skip_value}"

        return limit_clause


class SQLTranslator:
    """
    Unified SQL translator that can be used for both direct SQL generation
    and temporary table generation.

    This class provides a high-level interface for translating MongoDB-style query
    operations into SQL clauses. It integrates SQLFieldAccessor, SQLOperatorTranslator,
    and SQLClauseBuilder to provide comprehensive SQL translation capabilities.
    """

    def __init__(
        self,
        table_name: str | None = None,
        data_column: str = "data",
        id_column: str = "id",
        jsonb_supported: bool = False,
    ):
        """
        Initialize the SQLTranslator with table and column names.

        Args:
            table_name: The name of the table to query (default: "collection")
            data_column: The name of the column containing JSON data (default: "data")
            id_column: The name of the column containing document IDs (default: "id")
            jsonb_supported: Whether JSONB functions are supported (default: False)
        """
        self.table_name = table_name or "collection"
        self.data_column = data_column
        self.id_column = id_column
        self.jsonb_supported = jsonb_supported

        # Initialize components
        self.field_accessor = SQLFieldAccessor(
            data_column, id_column, jsonb_supported
        )
        self.operator_translator = SQLOperatorTranslator(self.field_accessor)
        self.clause_builder = SQLClauseBuilder(
            self.field_accessor, self.operator_translator
        )

    def translate_match(
        self, match_spec: Dict[str, Any], context: str = "direct"
    ) -> Tuple[str | None, List[Any]]:
        """
        Translate a $match stage to SQL WHERE clause.

        This method translates a MongoDB $match specification into an SQL WHERE clause.
        It handles special cases like text search queries by returning None to indicate
        that fallback to Python implementation is required. For regular queries, it delegates
        to the SQLClauseBuilder's build_where_clause method.

        Args:
            match_spec: The $match specification
            context: The context for field access (default: "direct")

        Returns:
            Tuple of (WHERE clause, parameters) or (None, []) for text search
        """
        # Handle text search queries separately
        if not isinstance(match_spec, dict):
            return _text_search_fallback()  # Fallback for non-dict queries

        if "$text" in match_spec:
            return (
                _text_search_fallback()
            )  # Special handling required, return None to fallback

        # Check for nested $text operators in logical operators
        if self._contains_text_operator(match_spec):
            return (
                _text_search_fallback()
            )  # Special handling required, return None to fallback

        # Pass the query to the clause builder so it can be used for field access decisions
        return self.clause_builder.build_where_clause(
            match_spec, context, query_param=match_spec
        )

    def _contains_text_operator(self, query: Dict[str, Any]) -> bool:
        """
        Check if a query contains any $text operators, including nested in logical operators.

        This method recursively traverses a MongoDB query specification to detect the presence
        of $text operators, which require special handling and fallback to Python implementation.
        It checks both top-level $text operators and those nested within logical operators
        ($and, $or, $nor, $not).

        Args:
            query: The query to check

        Returns:
            True if the query contains $text operators, False otherwise
        """
        for field, value in query.items():
            if field in ("$and", "$or", "$nor"):
                # Check each condition in logical operators
                if isinstance(value, list):
                    for condition in value:
                        if isinstance(
                            condition, dict
                        ) and self._contains_text_operator(condition):
                            return True
            elif field == "$not":
                # Check the condition in $not operator
                if isinstance(value, dict) and self._contains_text_operator(
                    value
                ):
                    return True
            elif field == "$text":
                # Found a $text operator
                return True
        return False

    def translate_sort(
        self, sort_spec: Dict[str, Any], context: str = "direct"
    ) -> str:
        """
        Translate a $sort stage to SQL ORDER BY clause.

        This method translates a MongoDB $sort specification into an SQL ORDER BY clause.
        It delegates to the SQLClauseBuilder's build_order_by_clause method to perform
        the actual translation, handling multiple sort fields with their respective
        sort directions (ascending or descending).

        Args:
            sort_spec: The $sort specification
            context: The context for field access (default: "direct")

        Returns:
            ORDER BY clause
        """
        return self.clause_builder.build_order_by_clause(sort_spec, context)

    def translate_skip_limit(
        self, limit_value: int | None = None, skip_value: int = 0
    ) -> str:
        """
        Translate $skip and $limit stages to SQL LIMIT/OFFSET clauses.

        This method translates MongoDB $skip and $limit specifications into SQL LIMIT and OFFSET clauses.
        It delegates to the SQLClauseBuilder's build_limit_offset_clause method to perform the actual
        translation, handling both limit and skip values appropriately for SQLite syntax.

        Args:
            limit_value: The limit value (default: None)
            skip_value: The skip value (default: 0)

        Returns:
            LIMIT and OFFSET clauses
        """
        return self.clause_builder.build_limit_offset_clause(
            limit_value, skip_value
        )

    def translate_field_access(
        self, field: str, context: str = "direct"
    ) -> str:
        """
        Translate field access for a given field and context.

        This method generates the appropriate SQL expression for accessing a field
        based on the field name and context. It delegates to the SQLFieldAccessor's
        get_field_access method to perform the actual translation, handling special
        cases like the "_id" field which maps to the ID column, and regular fields
        which use json_extract expressions.

        Args:
            field: The field name
            context: The context for field access (default: "direct")

        Returns:
            SQL expression for accessing the field
        """
        return self.field_accessor.get_field_access(field, context)

    def translate_sort_skip_limit(
        self,
        sort_spec: Dict[str, Any] | None,
        skip_value: int = 0,
        limit_value: int | None = None,
        context: str = "direct",
    ) -> Tuple[str, str, str]:
        """
        Translate sort/skip/limit stages to SQL clauses.

        This method translates MongoDB sort, skip, and limit specifications into their
        corresponding SQL clauses. It combines the functionality of translate_sort and
        translate_skip_limit to generate ORDER BY, LIMIT, and OFFSET clauses in a single call.

        Args:
            sort_spec: The $sort specification (default: None)
            skip_value: The skip value (default: 0)
            limit_value: The limit value (default: None)
            context: The context for field access (default: "direct")

        Returns:
            Tuple of (ORDER BY clause, LIMIT clause, OFFSET clause)
        """
        # Build ORDER BY clause
        order_by = self.translate_sort(sort_spec, context) if sort_spec else ""

        # Build LIMIT/OFFSET clause
        limit_offset = self.translate_skip_limit(limit_value, skip_value)

        return order_by, limit_offset, ""
