from decimal import Decimal
from typing import Any, Union

from src.utils.exception_utils import TokenArithmeticException


class Token:
    name: str
    symbol: str
    min_size: Decimal

    def __init__(self, **params):
        self.name = params['name']
        self.symbol = params['symbol']
        self.min_size = Decimal(str(params['min_size']))

    def __eq__(self, other: "Token") -> bool:
        if isinstance(other, Token):
            return self.symbol == other.symbol
        return NotImplemented

    def __str__(self):
        return f"{self.symbol}".upper()

    def __repr__(self):
        return f"Token[{self.symbol.upper()}]"


class Pair:
    base: Token  # BTC
    quote: Token  # USD

    def __init__(self, base, quote):
        self.base = base
        self.quote = quote

    def __str__(self):
        return f"{self.base.symbol}{self.quote.symbol}".upper()

    def __repr__(self):
        return f"Pair[{self.base.symbol}{self.quote.symbol}]"

    @property
    def inverse(self):
        return Pair(self.quote, self.base)


class PairSpotPrice:
    pair: Pair
    price: Decimal

    def __init__(self, **params):
        self.pair: Pair = params['pair']
        self.price = Decimal(str(params['price'])).quantize(self.pair.quote.min_size)

    @property
    def inverse_price(self) -> Decimal:
        return self.price ** -1

    def __str__(self):
        return f"1 {self.pair.base} = {self.price} {self.pair.quote}"

    def __repr__(self) -> str:
        return f"PairSpotPrice[1 {self.pair.base} = {self.price} {self.pair.quote}]"

    def __eq__(self, other: "PairSpotPrice") -> bool:
        return self.pair == other.pair and self.price == other.price

    def __add__(self, other: "PairSpotPrice") -> "PairSpotPrice":
        if not isinstance(other, PairSpotPrice):
            raise TokenArithmeticException(f"Unsopported operand type(s) for +: 'PairSpotPrice' and '{type(other)}'")
        if not self.pair == other.pair:
            raise TokenArithmeticException(f"Unsopported operand type(s) for +: '{self.pair}' and '{other.pair}'")
        return PairSpotPrice(pair=self.pair, price=self.price + other.price)

    def __radd__(self, other: Any):
        raise TokenArithmeticException(f"Unsopported operand type(s) for +: '{type(other)}' and '{type(self)}'")

    def __sub__(self, other: "PairSpotPrice") -> "PairSpotPrice":
        if not isinstance(other, PairSpotPrice):
            raise TokenArithmeticException(f"Unsopported operand type(s) for -: 'PairSpotPrice' and '{type(other)}'")
        if not self.pair == other.pair:
            raise TokenArithmeticException(f"Unsopported operand type(s) for -: '{self.pair}' and '{other.pair}'")
        return self + (-1 * other)

    def __rsub__(self, other: Any):
        raise TokenArithmeticException(f"Unsopported operand type(s) for -: '{type(other)}' and '{type(self)}'")

    def __mul__(self, other: Union[int, float, str, Decimal]) -> "PairSpotPrice":
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, str) or isinstance(other, Decimal):
            return PairSpotPrice(pair=self.pair, price=self.price * Decimal(f"{other}"))
        else:
            raise TokenArithmeticException(f"Unsopported operand type(s) for *: '{type(self)}' and '{type(other)}'")

    def __rmul__(self, other: Union[int, float, str, Decimal]) -> "PairSpotPrice":
        return self * other

    def __truediv__(self, other: Union[str, int, float, Decimal, "PairSpotPrice"]) -> Union["PairSpotPrice", Decimal]:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, str) or isinstance(other, Decimal):
            return PairSpotPrice(pair=self.pair, price=self.price / Decimal(f"{other}"))
        elif isinstance(other, PairSpotPrice):
            if not self.pair == other.pair:
                raise TokenArithmeticException(f"Unsopported operand type(s) for /: '{self.pair}' and '{other.pair}'")
            return self.price / other.price
        else:
            raise TokenArithmeticException(f"Unsopported operand type(s) for /: '{type(self)}' and '{type(other)}'")

    def __rtruediv__(self, other: Any):
        raise TokenArithmeticException(f"Unsopported operand type(s) for /: '{type(other)}' and '{type(self)}'")


class TokenAmount:
    token: Token
    amount: Decimal

    def __init__(self, token: Token, amount: Union[int, float, str, Decimal]):
        self.token = token
        self.amount = Decimal(str(amount)).quantize(token.min_size)

    def __str__(self):
        return f"{self.amount} {self.token}"

    def __repr__(self):
        return f"TokenAmount[{self.amount} {self.token}]"

    def __eq__(self, other: "TokenAmount") -> bool:
        return self.token == other.token and self.amount == other.amount

    def __add__(self, other: "TokenAmount") -> "TokenAmount":
        if not isinstance(other, TokenAmount):
            raise TokenArithmeticException(f"Unsopported operand type(s) for +: 'TokenAmount' and '{type(other)}'")
        if not self.token == other.token:
            raise TokenArithmeticException(f"Unsopported operand type(s) for +: '{self.token}' and '{other.token}'")
        return TokenAmount(self.token, self.amount + other.amount)

    def __radd__(self, other: "TokenAmount") -> "TokenAmount":
        return self + other

    def __sub__(self, other: "TokenAmount") -> "TokenAmount":
        if not isinstance(other, TokenAmount):
            raise TokenArithmeticException(f"Unsopported operand type(s) for -: 'TokenAmount' and '{type(other)}'")
        if not self.token == other.token:
            raise TokenArithmeticException(f"Unsopported operand type(s) for -: '{self.token}' and '{other.token}'")
        return self + (-1 * other)

    def __rsub__(self, other: "TokenAmount") -> "TokenAmount":
        return (-1 * self) + other

    def __mul__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> "TokenAmount":
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, str) or isinstance(other, Decimal):
            return TokenAmount(self.token, self.amount * Decimal(f"{other}"))
        elif isinstance(other, PairSpotPrice):
            if not self.token == other.pair.base:
                raise TokenArithmeticException(f"Unsopported operand type(s) for *: '{self.token}' and '{other.pair.base}'")
            return TokenAmount(other.pair.quote, self.amount * other.price)
        else:
            raise TokenArithmeticException(f"Unsopported operand type(s) for *: 'TokenAmount' and '{type(other)}'")

    def __rmul__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> Decimal:
        return self * other

    def __truediv__(self, other: Union[str, int, float, Decimal, "TokenAmount", PairSpotPrice]) -> Union["TokenAmount", Decimal]:
        if isinstance(other, int) or isinstance(other, float) or isinstance(other, str) or isinstance(other, Decimal):
            return TokenAmount(self.token, self.amount / Decimal(f"{other}"))
        elif isinstance(other, PairSpotPrice):
            if not self.token == other.pair.quote:
                raise TokenArithmeticException(f"Unsopported operand type(s) for /: '{self.token}' and '{other.pair.quote}'")
            return TokenAmount(other.pair.base, self.amount / other.price)
        elif isinstance(other, TokenAmount):
            if not self.token == other.token:
                raise TokenArithmeticException(f"Unsopported operand type(s) for /: '{self.token}' and '{other.token}'")
            return self.amount / other.amount
        else:
            raise TokenArithmeticException(f"Unsopported operand type(s) for *: 'TokenAmount' and '{type(other)}'")

    def __rtruediv__(self, other: Any):
        raise TokenArithmeticException(f"Unsopported operand type(s) for *: 'TokenAmount' and '{type(other)}'")
