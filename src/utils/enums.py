from datetime import datetime
from decimal import Decimal
from enum import Enum

from src import settings
from src.utils.exception_utils import TimeUnitNotSupportedException


class PivotTypeEnum(Enum):
    HIGH = 'high'
    LOW = 'low'


class TrendDirectionEnum(Enum):
    BULLISH = 'bullish'
    BEARISH = 'bearish'


class TrendTypeEnum(Enum):
    HIGHER_HIGH = 'HH'
    HIGHER_LOW = 'HL'
    LOWER_LOW = 'LL'
    LOWER_HIGH = 'LH'

    def __str__(self):
        return self.name.replace("_", "-").lower()


class OrderTypeEnum(Enum):
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP_LOSS = 'STOP_LOSS'
    STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
    TAKE_PROFIT = 'TAKE_PROFIT'
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
    TAKE_PROFIT_STOP_LOSS_LIMIT = 'TAKE_PROFIT_STOP_LOSS_LIMIT'

    def __str__(self):
        return self.name.replace("_", "-").lower()


class OrderDirectionEnum(Enum):
    # LONG = 'LONG'
    # SHORT = 'SHORT'
    BUY = 1
    SELL = -1
    HODL = 0

    def __str__(self):
        return self.name.replace("_", "-").lower()

    def toggle(self):
        return OrderDirectionEnum.SELL if self.value > 0 else OrderDirectionEnum.BUY


class OrderStatusEnum(Enum):
    CREATED = 'CREATED'  # In portfolio
    OPENING = 'OPENING'
    OPEN = 'OPEN'  # In market
    CLOSING = 'CLOSING'
    CLOSED = 'CLOSED'
    CANCELING = 'CANCELING'
    CANCELED = 'CANCELED'


class QtyTypeEnum(Enum):
    PERCENTAGE = 'PERCENTAGE'
    CURRENCY = 'CURRENCY'

    def __str__(self):
        return self.name.lower()

    def toggle(self):
        return QtyTypeEnum.PERCENTAGE if self == QtyTypeEnum.CURRENCY else QtyTypeEnum.CURRENCY

    def is_valid(self, amount: Decimal) -> bool:
        if self == QtyTypeEnum.PERCENTAGE:
            return Decimal("0") <= amount <= Decimal("100")
        return amount >= Decimal("0")


class QtyUnitTypeEnum(Enum):
    BASE = 'BASE'
    QUOTE = 'QUOTE'

    def __str__(self):
        return self.name.lower()

    def toggle(self):
        return QtyUnitTypeEnum.BASE if self == QtyUnitTypeEnum.QUOTE else QtyUnitTypeEnum.QUOTE


class TimeUnitEnum(Enum):
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"

    def to_seconds(self) -> int:
        if self == TimeUnitEnum.SECOND:
            return 1
        elif self == TimeUnitEnum.MINUTE:
            return 60
        elif self == TimeUnitEnum.HOUR:
            return 60 * 60
        elif self == TimeUnitEnum.DAY:
            return 60 * 60 * 24
        elif self == TimeUnitEnum.WEEK:
            return 60 * 60 * 24 * 7
        elif self == TimeUnitEnum.MONTH:
            return 60 * 60 * 24 * 7 * 4
        elif self == TimeUnitEnum.YEAR:
            return 60 * 60 * 24 * 7 * 52


class TimeseriesPeriodEnum(Enum):
    ONE_HOURS = "1HRS"
    FOUR_HOURS = "4HRS"
    ONE_DAY = "1DAY"
    THREE_DAY = "3DAY"
    ONE_WEEK = "1WKS"
    ONE_MONTH = "1MNT"
    ONE_YEAR = "1YRS"

    def get_time_unit(self) -> TimeUnitEnum:
        if "SEC" in self.value:
            return TimeUnitEnum.SECOND
        elif "MIN" in self.value:
            return TimeUnitEnum.MINUTE
        elif "HRS" in self.value:
            return TimeUnitEnum.HOUR
        elif "DAY" in self.value:
            return TimeUnitEnum.DAY
        elif "WKS" in self.value:
            return TimeUnitEnum.WEEK
        elif "MNT" in self.value:
            return TimeUnitEnum.MONTH
        elif "YRS" in self.value:
            return TimeUnitEnum.YEAR
        else:
            raise TimeUnitNotSupportedException()

    def get_period_value(self) -> int:
        return int(self.value[:-3])

    def get_period_value_sec(self) -> int:
        return self.get_period_value() * self.get_time_unit().to_seconds()

    def get_period_value_hours(self) -> int:
        return int(self.get_period_value_sec() / 3600)


class TimeseriesHorizonEnum(Enum):
    YEAR_TO_DATE = "YTD"
    QUARTER_TO_DATE = "QTD"
    MONTH_TO_DATE = "MTD"
    WEEK_TO_DATE = "WTD"
    INCEPTION = "INC"
    HALVENING = "HLV"

    def __str__(self):
        return self.name.lower()

    def get_horizon_start_date(self, to_date: datetime = None):
        to_date = datetime.utcnow() if not to_date else to_date
        if self == TimeseriesHorizonEnum.YEAR_TO_DATE:
            return datetime.combine(to_date.replace(month=1, day=1), datetime.min.time())
        elif self == TimeseriesHorizonEnum.QUARTER_TO_DATE:
            month = to_date.month % 4 + 1
            return datetime.combine(to_date.replace(month=month, day=1), datetime.min.time())
        elif self == TimeseriesHorizonEnum.MONTH_TO_DATE:
            return datetime.combine(to_date.replace(day=1), datetime.min.time())
        elif self == TimeseriesHorizonEnum.WEEK_TO_DATE:
            raise NotImplementedError()
        elif self == TimeseriesHorizonEnum.INCEPTION:
            return settings.BIG_BANG_DATE
        elif self == TimeseriesHorizonEnum.HALVENING:
            raise NotImplementedError()
        else:
            raise TimeUnitNotSupportedException()


class AnalysisTypeEnum(Enum):
    LOGARITHMIC_REGRESSION = "logarithmic_regression"
