from datetime import datetime
from decimal import Decimal
from typing import Union


def to_decimal_old(value: Union[int, float, str, Decimal, None], precision: int = None) -> Union[Decimal, None]:
    if not value:
        return None
    value = Decimal(value)
    if precision:
        value = round(value, precision)
    return value


def timestamp_to_datetime(ts: Union[str, int]) -> datetime:
    ts = int(ts)
    return datetime.fromtimestamp(ts)


def datetime_to_timestamp(dt: datetime) -> int:
    return int(datetime.timestamp(dt))
