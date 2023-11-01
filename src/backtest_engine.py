import copy
from datetime import datetime, timedelta
import time
from typing import List

import pandas as pd
from tqdm import tqdm

from src.markets.mock_market import MockMarket
from src.models.strategy import StrategyAction, StrategyTestResult
from src.models.token import Pair
from src.models.user import AccountBalance
from src.services import formula_service
from src.strategies.base_strategy import Strategy
from src.utils import enums, timeseries_utils


class TestResult:
    execution_date: datetime
    balance: AccountBalance
    action: StrategyAction

    def __init__(self, **params):
        self.execution_date = params['execution_date']
        self.balance = params['balance']
        self.action = params['action']

    def __iter__(self):
        yield "execution_date", self.execution_date
        for k, v in self.balance:
            yield (k, v)
        yield "action", str(self.action.direction)


class StrategyTester:
    test_date_start: datetime
    test_date_end: datetime
    period: enums.TimeseriesPeriodEnum
    strategy: Strategy
    pair: Pair
    market: MockMarket
    results: List[TestResult]

    def __init__(self, **params):
        self.test_date_start = params.get('start_test_date', datetime(2018, 1, 1))
        self.test_date_end = min(params.get('end_test_date', datetime.utcnow()), datetime.utcnow())
        self.period = params.get('period', enums.TimeseriesPeriodEnum.ONE_HOURS)
        self.strategy = params['strategy']
        self.pair = params['pair']
        self.market = MockMarket(params.get('initial_balance'))
        self.results = []

    def start_strategy_test(self, **params) -> List[TestResult]:
        end_date = timeseries_utils.get_previous_period_end(self.test_date_end, self.period)
        date_range = timeseries_utils.get_period_range(self.test_date_start, end_date, self.period)
        
        with tqdm(total=100, miniters=1) as pbar:
            for execution_date in (self.test_date_start + timedelta(seconds=n) for n in date_range):
                # update mrkt
                # create action
                action = self.strategy.execute(pair=self.pair, execute_date=execution_date, **params)
                # action to order
                order = self.strategy.action_to_order(action)
                # execute order on mrkt
                created_order = self.market.add_order(execution_date=execution_date, order=order)
                # get balance
                account_balance: AccountBalance = self.market.get_account_balance(execution_date=execution_date)
                execution_date_cp = copy.deepcopy(execution_date)
                account_balance_cp = copy.deepcopy(account_balance)
                action_cp = copy.deepcopy(action)
                # append test result
                test_res = TestResult(execution_date=execution_date_cp, balance=account_balance_cp, action=action_cp)
                self.results.append(test_res)
                pbar.update(date_range.step / date_range.stop * 100)

        return self.results

    def test_result_to_df(self, test_result: List[TestResult] = None) -> pd.DataFrame:
        if not test_result:
            test_result = self.results
        return pd.DataFrame([dict(r) for r in test_result])

    def evaluate_result(self, test_result: dict, **params) -> StrategyTestResult:
        result = StrategyTestResult(test_result)
        horizon: enums.TimeseriesHorizonEnum = params.get('horizon')
        test_result_series = self.test_result_to_df(test_result)
        setattr(result, str(horizon), formula_service.get_time_weighted_rate_of_return(test_result_series, horizon))
        return result
