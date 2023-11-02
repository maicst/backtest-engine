import copy
from decimal import Decimal
from typing import Union

from src.utils.exception_utils import TokenArithmeticsException


class Token:
    name: str
    symbol: str
    min_size: Decimal

    def __init__(self, **params):
        self.name = params['name']
        self.symbol = params['symbol']
        self.min_size = Decimal(str(params['min_size']))

    def __eq__(self, other: "Token") -> bool:
        """Overrides the default implementation"""
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

    def __str__(self):
        return f"1 {self.pair.base} = {self.price} {self.pair.quote}"

    def __repr__(self) -> str:
        return f"PairSpotPrice[1 {self.pair.base} = {self.price} {self.pair.quote}]"

    @property
    def inverse(self):
        i_pair = self.pair.inverse
        i_price = self.price ** -1
        return PairSpotPrice(pair=i_pair, price=i_price)


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

    @staticmethod
    def _safe_add(first: "TokenAmount", second: "TokenAmount") -> "TokenAmount":
        if not second.token == first.token:  # it works only on the same tokens
            raise TokenArithmeticsException(f"Can't sum {first.token} and {second.token}.")
        return TokenAmount(first.token, (first.amount + second.amount).quantize(first.token.min_size))

    @staticmethod
    def _safe_mul(first: "TokenAmount", second: Union[Decimal, PairSpotPrice]) -> "TokenAmount":
        if isinstance(second, Decimal):
            # TokenAmount[5 USD] x 2 = TokenAmount[10 USD]
            return TokenAmount(first.token, (first.amount * second).quantize(first.token.min_size))

        if isinstance(second, PairSpotPrice):
            # TokenAmount[1 BTC] x PairSpotPrice[100 USD x BTC] = TokenAmount[100 USD]
            if not first.token == second.pair.base:
                raise TokenArithmeticsException(f"Can't multiply {first.token} and {second.pair.base}.")

            exp = second.pair.quote.min_size
            return TokenAmount(second.pair.quote, (first.amount * second.price).quantize(exp))

    def __add__(self, other: "TokenAmount") -> "TokenAmount":
        if not isinstance(other, TokenAmount):
            raise TokenArithmeticsException()
        return self._safe_add(self, other)

    def __radd__(self, other: "TokenAmount") -> "TokenAmount":
        return self.__add__(other)

    def __sub__(self, other: "TokenAmount") -> "TokenAmount":
        if not isinstance(other, TokenAmount):
            raise TokenArithmeticsException()
        return self + (-1 * other)

    def __rsub__(self, other: "TokenAmount") -> "TokenAmount":
        if not isinstance(other, TokenAmount):
            raise TokenArithmeticsException()
        return other + (-1 * self)

    def __mul__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> "TokenAmount":
        second = copy.deepcopy(other)
        # Everything to Decimal
        if isinstance(second, str) or isinstance(second, int) or isinstance(second, float):
            second = Decimal(f"{second}")
        # Check type
        if not isinstance(second, Decimal) and not isinstance(second, PairSpotPrice):
            raise TokenArithmeticsException(f"Can't multiply {type(self)} x {type(second)}.")

        return self._safe_mul(self, second)

    def __rmul__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> Decimal:
        return self.__mul__(other)

    def __truediv__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> Decimal:
        second = copy.deepcopy(other)
        # Everything to Decimal
        if isinstance(second, str) or isinstance(second, int) or isinstance(second, float):
            second = Decimal(f"{second}")
        # Check type
        if not isinstance(second, Decimal) and not isinstance(second, PairSpotPrice):
            raise TokenArithmeticsException(f"Can't divide {type(self)} / {type(second)}.")
        if isinstance(second, PairSpotPrice):
            second = second.inverse  # NOTE using inverse cause loss of precision
            # second = second.price ** -1
        else:
            second = second ** (-1)
        return self._safe_mul(self, second)

    def __rtruediv__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> Decimal:
        second = copy.deepcopy(self)
        if isinstance(second, str) or isinstance(second, int) or isinstance(second, float):
            raise TokenArithmeticsException()
        if isinstance(other, PairSpotPrice):
            raise NotImplementedError()
        return self._safe_mul(other, second)
