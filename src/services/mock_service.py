import json
from datetime import datetime
from decimal import Decimal
from typing import List

import pandas as pd

from src import settings
from src.models.mock_user import MockAccountBalance
from src.models.order import Order
from src.models.token import Pair, PairSpotPrice
from src.models.user import TokenAmount
from src.utils import price_utils, enums, token_utils
from src.utils.exception_utils import MissingExecutionDateException, OrderTypeNotSupportedException, \
    OrderStatusNotSupportedException


def refresh_status(fn):
    def wrapper(*args, **kwargs):
        if not kwargs.get('execution_date'):
            raise MissingExecutionDateException()

        _self: MockService = args[0]
        if kwargs['execution_date'] >= _self.account_balance.update_date:
            # esistono ordini aperti?
            open_orders = _self._get_open_orders()
            for order in open_orders:
                if order.order_type == enums.OrderTypeEnum.MARKET:
                    _self._update_balance(order, kwargs['execution_date'])
                    order.status = enums.OrderStatusEnum.CLOSED
                elif order.order_type == enums.OrderTypeEnum.LIMIT:
                    candle = _self._get_price(kwargs['execution_date'])
                    if order.direction == enums.OrderDirectionEnum.BUY:
                        if order.price >= candle['Low']:
                            _self._update_balance(order, kwargs['execution_date'])
                            order.status = enums.OrderStatusEnum.CLOSED
                    elif order.direction == enums.OrderDirectionEnum.SELL:
                        if order.price <= candle['High']:
                            _self._update_balance(order, kwargs['execution_date'])
                            order.status = enums.OrderStatusEnum.CLOSED
                else:
                    raise OrderTypeNotSupportedException()
        return fn(*args, **kwargs)

    return wrapper


class MockService:
    prices: pd.DataFrame  # TODO {"BTCUSD": pd.DataFrame, "ETHUSD": pd.DataFrame, ...}
    account_balance: MockAccountBalance
    orders: List[Order]

    def __init__(self, initial_balance: dict = None):
        if initial_balance:
            balance_dict = initial_balance
        else:
            try:
                with open(settings.MOCK_BALANCE_CONFIG_FILE) as balance_file:
                    balance_dict = json.load(balance_file)
            except:
                balance_dict = settings.DEFAULT_MOCK_BALANCE
        balance = [TokenAmount(token_utils.get_token_info(token), amount) for token, amount in balance_dict.items()]
        self.account_balance = MockAccountBalance(balance)
        self.prices = price_utils.get_ohlc_prices()
        self.orders = []

    def _get_open_orders(self):
        return [o for o in self.orders if o.status == enums.OrderStatusEnum.OPEN]

    def _get_price(self, pair: Pair, dt: datetime) -> pd.Series:
        # TODO integrare pair
        norm_dt = dt.replace(minute=0, second=0, microsecond=0)
        return self.prices.loc[norm_dt]

    def _get_order_price(self, order: Order, dt: datetime) -> PairSpotPrice:
        candle = self._get_price(order.pair, dt)
        if order.order_type == enums.OrderTypeEnum.MARKET:
            spot_price = PairSpotPrice(pair=order.pair, price=candle.mean())
            return spot_price
        elif order.order_type == enums.OrderTypeEnum.LIMIT:
            return PairSpotPrice(pair=order.pair, price=order.price)

    def _update_balance(self, order: Order, execution_date: datetime):
        fee = Decimal("0")
        if order.direction == enums.OrderDirectionEnum.BUY:
            # case OPENING ORDER
            if order.status == enums.OrderStatusEnum.CREATED:
                token_symbol = order.pair.quote.symbol
                amount = order.qty_token_amount * self._get_order_price(order, execution_date) * -1
            # case CLOSING ORDER
            elif order.status == enums.OrderStatusEnum.OPEN:
                token_symbol = order.pair.base.symbol
                amount = order.qty_token_amount.amount
                fee = amount * (settings.MOCK_MARKET_FEE / Decimal("100"))
                amount -= fee
            else:
                raise OrderStatusNotSupportedException()
        elif order.direction == enums.OrderDirectionEnum.SELL:
            # case OPENING ORDER
            if order.status == enums.OrderStatusEnum.CREATED:
                token_symbol = order.pair.base.symbol
                amount = -1 * order.qty_token_amount
            # case CLOSING ORDER
            elif order.status == enums.OrderStatusEnum.OPEN:
                token_symbol = order.pair.quote.symbol
                amount = order.qty_token_amount * self._get_order_price(order, execution_date)
                fee = amount * (settings.MOCK_MARKET_FEE / Decimal("100"))
                amount -= fee
            else:
                raise OrderStatusNotSupportedException()
        else:
            raise OrderTypeNotSupportedException()
        # TODO passare direttamente token_amount
        self.account_balance.update_balance(token_symbol, amount, execution_date)

    @refresh_status
    def get_account_balance(self, execution_date) -> MockAccountBalance:
        return self.account_balance

    @refresh_status
    def get_open_orders(self, execution_date, **params) -> List[Order]:
        return self._get_open_orders()

    @refresh_status
    def get_orders_info(self, execution_date, **params) -> List[Order]:
        ids = params['order_ids']
        result = []
        for id in ids:
            res = next((o for o in self.orders if o.order_id == id), None)
            if res:
                result.append(res)
        return result

    @refresh_status
    def add_order(self, execution_date, **params) -> Order:
        order = params['order']
        order.set_order_id("MOCK_ORDER")
        self._update_balance(order, execution_date)
        order.status = enums.OrderStatusEnum.OPEN
        if order.order_type == enums.OrderTypeEnum.MARKET:
            self._update_balance(order, execution_date)
            order.status = enums.OrderStatusEnum.CLOSED
        self.orders.append(order)
        return order

    def get_instant_price(self, pair: Pair, execution_date: datetime = datetime.utcnow()) -> PairSpotPrice:
        spot_price = PairSpotPrice(pair=pair, price=self._get_price(pair, execution_date).mean())
        return spot_price
