import random
from abc import ABC, abstractmethod
from datetime import datetime

from src.models.order import Order
from src.models.strategy import StrategyAction
from src.models.token import Pair
from src.utils import enums


class Strategy(ABC):
    execute_date: datetime
    pair: Pair

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def _execute(self, **params) -> StrategyAction:
        pass

    @abstractmethod
    def action_to_order(self, action: StrategyAction) -> Order:
        raise NotImplementedError('not implemented')

    def execute(self, **params) -> StrategyAction:
        self.execute_date = params.pop('execute_date')
        self.pair = params.pop('pair')
        return self._execute(**params)


class HodlStrategy(Strategy):
    def _execute(self, **params) -> StrategyAction:
        action = StrategyAction(pair=self.pair, direction=enums.OrderDirectionEnum.HODL)
        return action

    def action_to_order(self, action: StrategyAction) -> Order:
        return Order(**dict(action))


class DollarCostAveragingStrategy(Strategy):
    def _execute(self, **params) -> StrategyAction:
        # Buy at random hour of the day
        today = datetime.utcnow()
        random_hour = random.randint(0, 23)
        if today.date() == self.execute_date.date():
            random_hour = random.randint(0, min(max(0, today.hour - 1), 23))
        self.execute_date = self.execute_date.replace(hour=random_hour)
        action = StrategyAction(pair=self.pair,
                                direction=enums.OrderDirectionEnum.BUY,
                                order_type=enums.OrderTypeEnum.MARKET,
                                qty="50",
                                qty_unit_type=enums.QtyUnitTypeEnum.QUOTE,
                                qty_type=enums.QtyTypeEnum.CURRENCY,
                                exec_dt=self.execute_date)
        return action

    def action_to_order(self, action: StrategyAction) -> Order:
        return Order(**dict(action))
