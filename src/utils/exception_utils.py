# GENERAL
class MissingExecutionDateException(BaseException):
    pass


class TimeUnitNotSupportedException(BaseException):
    pass


class InvalidQuantityException(BaseException):
    pass


# PORTFOLIO/ACCOUNT BALANCE
class NotEnoughMoneyException(BaseException):
    pass


# ORDER
class OrderDoesNotExistException(BaseException):
    pass


class OrderTypeNotSupportedException(BaseException):
    pass


class OrderStatusNotSupportedException(BaseException):
    pass


# TOKEN
class UnknownTokenException(BaseException):
    pass
