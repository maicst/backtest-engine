import json
from datetime import datetime

import pandas as pd


def get_recovery_df():
    with open("resources/BTCUSD_20231030.json", "r") as f:
        p = json.load(f)
    [i.update(i['o']) for i in p]  # format
    df = pd.DataFrame(p)
    df['t'] = df['t'].apply(lambda x: datetime.fromtimestamp(x))
    rename_cols = {"t": "date", "o": "open", "h": "high", "l": "low", "c": "close"}
    df = df.rename(columns=rename_cols)
    df = df.set_index('date')
    df = df.loc[(df.index >= datetime(2011, 9, 1))]  # where nans disappear
    return df


if __name__ == '__main__':
    print("Start")
    df = pd.read_csv("resources/crypto_price_202310282152.csv")
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    
    rec_df = get_recovery_df()
    rec_df = rec_df.tz_localize('Europe/Rome', ambiguous='infer').tz_convert(None) # To UTC and remove tz
    
    # fill prices
    rec_df.loc[rec_df[rec_df['open'].isna()].index, :] = df.loc[rec_df[rec_df['open'].isna()].index, ['open', 'high', 'low', 'close']]
    # r_diff = df['date'].diff().iloc[1:].apply(lambda x: x.value / (60 * 60 * 10**9))
    rec_df = rec_df.reset_index()
    pd.to_pickle(rec_df, "resources/BTCUSD_price.pickle")
    print("Done")
