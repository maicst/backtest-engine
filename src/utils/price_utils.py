import base64
import json
from datetime import datetime

import boto3
import pandas as pd

from src import settings
from src.models.token import Pair
from src.utils import enums, token_utils

DEFAULT_PAIR = token_utils.PairFactory().get_pair_by_name("BTC", settings.ACCOUNT_BALANCE_CURRENCY)


def get_ohlc_prices(pair: Pair = DEFAULT_PAIR, from_dt: datetime = None, to_dt: datetime = None) -> pd.DataFrame:
    df = pd.read_pickle("resources/BTCUSD_price.pickle")
    df = df[['date', 'open', 'high', 'low', 'close']]
    df['date'] = pd.to_datetime(df['date'])
    rename_cols = {'date': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'}
    df.rename(columns=rename_cols, inplace=True)
    df = df.set_index('Date')
    if from_dt:
        df = df.loc[:from_dt]
    if to_dt:
        df = df.loc[to_dt:]
    return df


def get_prices(pair, period, from_dt, to_dt):
    client = boto3.client('lambda', region_name='eu-west-1')
    FIND_PRICES = "CryptoApp-FindPrices"
    body = {
        "pair_name": str(pair),
        "period": period.value
    }
    if from_dt:
        body.update({
            "from_dt": str(from_dt)
        })
    if to_dt:
        body.update({
            "to_dt": str(to_dt)
        })
    context = json.dumps({"user": "me"}).encode('utf-8')
    response = client.invoke(
        FunctionName=FIND_PRICES,
        InvocationType='RequestResponse',
        LogType='None',
        ClientContext=base64.b64encode(context).decode('utf-8'),
        Payload=json.dumps(body)
    )
    res = json.loads(response["Payload"].read())
    if not res.get("errorMessage"):
        return pd.DataFrame(res['body'])


def get_prices_controller(pair: Pair = DEFAULT_PAIR,
                          period: enums.TimeseriesPeriodEnum = enums.TimeseriesPeriodEnum.ONE_HOURS,
                          from_dt: datetime = None, to_dt: datetime = None) -> pd.DataFrame:
    return get_prices(pair, period, from_dt, to_dt)
