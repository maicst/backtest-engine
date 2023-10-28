from decimal import Decimal

import pandas as pd
from ta import momentum, trend, volatility

from src.utils.enums import PivotTypeEnum, TimeseriesHorizonEnum


def get_rate_of_return(start_value: Decimal, end_value: Decimal) -> Decimal:
    rr = 0
    if start_value != 0:
        rr = (end_value - start_value) / start_value
    return rr


# TIME WEIGHTED = [..., t-1, t, ...] in respect of a date
def get_time_weighted_rate_of_return(values: pd.Series, horizon: TimeseriesHorizonEnum):
    rr = {}
    for dt, val in values.iteritems():
        start_dt = horizon.get_horizon_start_date(dt)
        try:
            start_val = values.loc[start_dt]
        except KeyError:
            start_val = Decimal("0")
        rr[dt] = get_rate_of_return(start_val, val)
    return pd.Series(rr)


# ROLLING = [..., t-1, t, ...] in respect of [..., t-1-period, t-period, ...]
def get_rolling_rate_of_return(values: pd.Series, period: int = 1) -> pd.Series:
    if period < 1:
        period = 1
    rr: pd.Series = values.rolling(window=period + 1, min_periods=0).apply(lambda x: get_rate_of_return(x[0], x[-1]))
    rr.name = "value"
    return rr


def get_ema(values: pd.Series, window: int = 21, fillna=True) -> pd.Series:
    return trend.ema_indicator(values, window=window, fillna=fillna)


def get_ma(values: pd.Series, window: int = 21, fillna=True) -> pd.Series:
    return trend.sma_indicator(values, window=window, fillna=fillna)


def get_rsi(values: pd.Series, window: int = 14) -> pd.Series:
    return momentum.rsi(values, window=window, fillna=True)


def get_stoch(hlc_values: pd.DataFrame,
              close_col: str = 'Close', high_col: str = 'High', low_col: str = 'Low',
              window: int = 14) -> pd.DataFrame:
    close_ser = hlc_values[close_col]
    high_ser = hlc_values[high_col]
    low_ser = hlc_values[low_col]
    stoch_val: pd.Series = momentum.stoch(close_ser, high_ser, low_ser, window=window, fillna=True)
    stoch_signal_val: pd.Series = momentum.stoch_signal(close_ser, high_ser, low_ser, window=window, fillna=True)
    frame = {'Stoch': stoch_val, 'Stoch Signal': stoch_signal_val}
    return pd.DataFrame(frame)


# Average True Range # TODO write ExponentialAverage True Range
# https://medium.com/swlh/the-supertrend-indicator-in-python-coding-and-back-testing-its-strategy-e37d631c33f
def get_atr(hlc_values: pd.DataFrame,
            close_col: str = 'Close', high_col: str = 'High', low_col: str = 'Low',
            window: int = 14):
    close_ser = hlc_values[close_col]
    high_ser = hlc_values[high_col]
    low_ser = hlc_values[low_col]
    return volatility.average_true_range(close_ser, high_ser, low_ser, window=window, fillna=True)


def get_pivot(ts: pd.Series, pivot_type: PivotTypeEnum = None, neighborhood: int = 5) -> pd.Series:
    neighborhood = neighborhood * 2 + 1
    if pivot_type == PivotTypeEnum.HIGH:
        pivot: pd.Series = ts.rolling(window=neighborhood, center=True, min_periods=0).max()
    elif pivot_type == PivotTypeEnum.LOW:
        pivot: pd.Series = ts.rolling(window=neighborhood, center=True, min_periods=0).min()
    else:
        raise Exception('type must be specified')

    return pivot == ts


def normalize_dataframe_columns(df: pd.DataFrame, col_name: str) -> pd.Series:
    df_copy = df.copy()
    return (df_copy[col_name] - df_copy[col_name].min()) / (df_copy[col_name].max() - df_copy[col_name].min())
