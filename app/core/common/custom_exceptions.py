class RequestError(Exception):
    pass


class MissingToken(Exception):
    pass


class InvalidToken(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class StillProcessing(Exception):
    pass
