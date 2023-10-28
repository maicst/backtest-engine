from datetime import datetime
from decimal import Decimal
from typing import List

from src import settings
from src.connections.mock_connection import MockConnector
from src.markets.interface import MarketInterface
from src.models.order import Order
from src.models.token import Pair, TokenAmount, Token
from src.models.user import AccountBalance
from src.utils import enums
from src.utils.exception_utils import InvalidQuantityException


class MockMarket(MarketInterface):
    connector: MockConnector

    def __init__(self, initial_balance: dict = None):
        self.connector = MockConnector(initial_balance)

    def get_account_balance(self, **params) -> AccountBalance:
        account_balance = self.connector.get_account_balance(execution_date=params.get('execution_date'))
        account_balance.value = self.get_account_balance_value(account_balance, execution_date=params['execution_date'])
        return account_balance

    def get_account_balance_value(self, account_balance: AccountBalance, execution_date: datetime) -> Decimal:
        total_value = Decimal("0")
        for balance in account_balance.balance:
            if balance.token.symbol == settings.ACCOUNT_BALANCE_CURRENCY:
                last_price = Decimal("1")
            else:
                pair = Pair(balance.token, settings.ACCOUNT_BALANCE_CURRENCY_TOKEN_INFO)
                last_price = self.connector.get_instant_price(pair=pair, execution_date=execution_date)
            total_value += last_price * balance
        return total_value

    def get_open_orders(self, **params) -> List[Order]:
        return self.connector.get_open_orders(**params)

    def get_orders_info(self, execution_date: datetime, order_ids: List[str] = None) -> List[Order]:
        return self.connector.get_orders_info(execution_date=execution_date, order_ids=order_ids)

    def add_order(self, execution_date: datetime, order: Order):
        if order.direction == enums.OrderDirectionEnum.HODL:
            return order
        self.normalize_input_order(order=order, execution_date=execution_date)
        if order.qty == Decimal("0"):
            return order
        return self.connector.add_order(execution_date=execution_date, order=order)

    def normalize_input_order(self, **params) -> Order:
        order = super().normalize_input_order(**params)
        # initialize token amount for base currency
        order.qty_token_amount = TokenAmount(order.pair.base, order.qty)
        return order

    def normalize_quantity(self, order: Order, execution_date: datetime):
        if not order.qty_type.is_valid(order.qty):
            raise InvalidQuantityException(f"{order.qty} is not a valid quantity for type {order.qty_type}.")
        # init token_amount
        if order.qty_unit_type == enums.QtyUnitTypeEnum.QUOTE:
            token_amount_quote = TokenAmount(order.pair.quote, order.qty)
            token_amount_base = TokenAmount(order.pair.base, "0")
        elif order.qty_unit_type == enums.QtyUnitTypeEnum.BASE:
            token_amount_quote = TokenAmount(order.pair.quote, "0")
            token_amount_base = TokenAmount(order.pair.base, order.qty)
        else:
            raise InvalidQuantityException(f"{order.qty_unit_type} is not a valid order.qty_unit_type")

        if order.qty_type == enums.QtyTypeEnum.PERCENTAGE:
            account_balance: AccountBalance = self.get_account_balance(execution_date=execution_date)
            token: Token = order.pair.__getattribute__(order.qty_unit_type.value.lower())
            balance = account_balance.get_token_amount_by_symbol(token.symbol)
            order.qty = order.qty / 100 * balance
            if order.qty_unit_type == enums.QtyUnitTypeEnum.QUOTE:
                token_amount_quote.amount = order.qty
            elif order.qty_unit_type == enums.QtyUnitTypeEnum.BASE:
                token_amount_base.amount = order.qty
            order.qty_type = order.qty_type.toggle()
        if order.qty_unit_type == enums.QtyUnitTypeEnum.QUOTE:
            pair_spot_price = self.connector.get_instant_price(pair=order.pair, execution_date=execution_date)
            token_amount_base.amount = token_amount_quote / pair_spot_price
            order.qty = token_amount_base.amount
            order.qty_unit_type = order.qty_unit_type.toggle()
