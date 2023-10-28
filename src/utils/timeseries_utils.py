from datetime import datetime, timedelta

from src.utils import enums
from src.utils.exception_utils import TimeUnitNotSupportedException

SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR


def get_previous_period_end(dt: datetime, period: enums.TimeseriesPeriodEnum) -> datetime:
    time_unit = period.get_time_unit()
    period_value = period.get_period_value()
    if time_unit == enums.TimeUnitEnum.SECOND:
        raise NotImplementedError('not implemented')
    elif time_unit == enums.TimeUnitEnum.MINUTE:
        raise NotImplementedError('not implemented')
    elif time_unit == enums.TimeUnitEnum.HOUR:
        new_hour = dt.hour
        while new_hour % period_value > 0:
            new_hour -= 1
        new_date = dt.replace(hour=new_hour, minute=0, second=0, microsecond=0)
    elif time_unit == enums.TimeUnitEnum.DAY:
        new_date = dt.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=period_value - 1)
    else:
        raise TimeUnitNotSupportedException()
    return new_date


def get_date_diff_in_sec(date_diff: timedelta):
    return date_diff.seconds + date_diff.days * SECONDS_IN_DAY


def get_period_range(start_date: datetime, end_date: datetime, period: enums.TimeseriesPeriodEnum) -> range:
    date_diff = end_date - start_date
    date_diff_sec = get_date_diff_in_sec(date_diff)
    step_sec = period.get_period_value_sec()
    return range(0, date_diff_sec + 1 * SECONDS_IN_HOUR, step_sec)  # + 1HRS in seconds
