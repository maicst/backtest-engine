from src.backtest_engine import StrategyTester
from src.utils.price_utils import get_ohlc_prices
from datetime import datetime

if __name__ == '__main__':
    px = get_ohlc_prices(from_dt=datetime(2013, 10, 3), to_dt=datetime(2017, 12, 6))
    StrategyTester()
