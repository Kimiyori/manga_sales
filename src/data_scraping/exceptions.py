class NotFound(Exception):
    """Not found 404"""


class Unsuccessful(Exception):
    """Fail to get respnse"""


class ConnectError(Exception):
    """Fail to connect"""


class IncorrectMethod(Exception):
    """Raises if passed incorrect method or attribute in list of commands in context manager"""


class BSError(Exception):
    """BeauitfulSoup parser error"""
