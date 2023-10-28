import datetime
from decimal import Decimal

from src.models.token import Pair
from src.utils import enums


class StrategyAction:
    pair: Pair
    direction: enums.OrderDirectionEnum  # BUY | SELL | HODL
    order_type: enums.OrderTypeEnum
    qty: Decimal
    qty_unit_type: enums.QtyUnitTypeEnum
    qty_type: enums.QtyTypeEnum
    price: Decimal
    exec_dt: datetime

    def __init__(self, **params):
        self.pair = params['pair']
        self.direction = params['direction']
        if self.direction != enums.OrderDirectionEnum.HODL:
            self.order_type = params['order_type']
            self.qty = Decimal(str(params['qty']))
            self.qty_unit_type = params.get('qty_unit_type', enums.QtyUnitTypeEnum.BASE)
            self.qty_type = params.get('qty_type', enums.QtyTypeEnum.CURRENCY)
            # if market order price is defined by market
            self.price = None if not params.get('price') else Decimal(str(params.get('price')))
            self.exec_dt = params.get("exec_dt", None)

    def __iter__(self):
        '''
        calling dict() returns kind-of-ready dict for order
        :return:
        '''
        yield "direction", self.direction
        yield "pair", self.pair
        if self.direction != enums.OrderDirectionEnum.HODL:
            yield "order_type", self.order_type
            yield "qty", self.qty
            yield "qty_unit_type", self.qty_unit_type
            yield "qty_type", self.qty_type
            yield "price", self.price
            yield "exec_dt", self.exec_dt


class StrategyTestResult:
    original: dict

    def __init__(self, original):
        self.original = original
