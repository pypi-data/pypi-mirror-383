class MalformedQueryException(Exception):
    """
    Exception raised when a query is malformed.
    """

    pass


class MalformedDocument(Exception):
    """
    Exception raised when a document is malformed.
    """

    pass


class CollectionInvalid(Exception):
    """
    Exception raised when a collection is invalid.
    """

    pass
