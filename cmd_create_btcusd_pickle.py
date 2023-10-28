import pandas as pd

if __name__ == '__main__':
    print("Start")
    df = pd.read_csv("resources/crypto_price_202310282152.csv")
    pd.to_pickle(df, "resources/BTCUSD_price.pickle")
    print("Done")
