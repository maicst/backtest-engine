from datetime import datetime
from decimal import Decimal

from src.models.token import Pair, TokenAmount
from src.utils import enums, type_utils


class PairOld:
    base: str  # BTC
    quote: str  # USD

    def __init__(self, base, quote):
        self.base = base
        self.quote = quote

    def __str__(self):
        return f"{self.base}{self.quote}".upper()


class Spread:
    ref_date: datetime
    buy_price: Decimal
    sell_price: Decimal

    def __init__(self, **params):
        self.ref_date = params['ref_date']
        self.buy_price = type_utils.to_decimal_old(params['buy_price'])
        self.sell_price = type_utils.to_decimal_old(params['sell_price'])


class OrderAdditionalInfo:
    qty_executed: Decimal
    cost: Decimal
    fee: Decimal
    exec_price: Decimal
    stop_price: Decimal
    limit_price: Decimal

    def __init__(self, **params):
        self.qty_executed = type_utils.to_decimal_old(params.get('qty_executed', 0))
        self.cost = type_utils.to_decimal_old(params.get('cost', 0))
        self.fee = type_utils.to_decimal_old(params.get('fee', 0))
        self.exec_price = type_utils.to_decimal_old(params.get('exec_price', 0))
        self.stop_price = type_utils.to_decimal_old(params.get('stop_price', 0))
        self.limit_price = type_utils.to_decimal_old(params.get('limit_price', 0))


class Order:
    # required
    pair: Pair
    direction: enums.OrderDirectionEnum  # BUY | SELL
    order_type: enums.OrderTypeEnum
    qty: Decimal
    qty_unit_type: enums.QtyUnitTypeEnum  # BASE | QUOTE
    qty_type: enums.QtyTypeEnum  # PERCENTAGE | CURRENCY
    # not required
    order_id: str = None
    open_time: datetime = None
    close_time: datetime = None
    price: Decimal = None
    price2: Decimal = None
    leverage: int = None
    start_time: datetime = None
    expire_time: datetime = None
    # defaulted
    status: enums.OrderStatusEnum
    info: OrderAdditionalInfo
    # generated
    qty_token_amount: TokenAmount = None

    def __init__(self, **params):
        self.pair = params['pair']
        self.direction = params['direction']
        if self.direction != enums.OrderDirectionEnum.HODL:
            self.order_type = params['order_type']
            self.qty = Decimal(str(params['qty']))
            self.qty_unit_type = params.get('qty_unit_type', enums.QtyUnitTypeEnum.BASE)
            self.qty_type = params.get('qty_type', enums.QtyTypeEnum.CURRENCY)
            self.open_time = params.get('open_time')
            self.close_time = params.get('close_time')
            self.price = type_utils.to_decimal_old(params.get('price'))
            self.price2 = type_utils.to_decimal_old(params.get('price2'))
            self.leverage = params.get('leverage')
            self.start_time = params.get('start_time')
            self.expire_time = params.get('expire_time')
            self.status = params.get('status', enums.OrderStatusEnum.CREATED)
            self.info = OrderAdditionalInfo(**params)

    def set_order_id(self, order_id):
        self.order_id = order_id
