from src import settings
from src.backtest_engine import StrategyTester
from src.models.token import Pair
from src.strategies.base_strategy import DollarCostAveragingStrategy
from src.utils import token_utils
from datetime import datetime

if __name__ == '__main__':
    # px = get_ohlc_prices(from_dt=datetime(2013, 10, 3), to_dt=datetime(2017, 12, 6))

    dca = DollarCostAveragingStrategy()
    pair = Pair(token_utils.get_token_info("BTC"), settings.ACCOUNT_BALANCE_CURRENCY_TOKEN_INFO)

    s_dt = datetime(2015, 10, 3)
    e_dt = datetime(2017, 12, 6)
    engine = StrategyTester(start_test_date=s_dt, end_test_date=e_dt, strategy=dca, pair=pair)
    r = engine.start_strategy_test()
