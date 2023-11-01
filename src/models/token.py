import copy
from decimal import Decimal
from typing import Union


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


class PairSpotPrice:
    pair: Pair
    price: Decimal

    def __init__(self, **params):
        self.pair: Pair = params['pair']
        self.price = Decimal(str(params['price'])).quantize(self.pair.quote.min_size)

    def __str__(self):
        return f"1 {self.pair.base} = {self.price} {self.pair.quote}"


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
    def _safe_add(first: Union[str, int, float, Decimal, "TokenAmount"],
                  second: Union[str, int, float, Decimal, "TokenAmount"]) -> Decimal:
        if isinstance(first, TokenAmount) and isinstance(second, TokenAmount):
            assert second.token == first.token  # it works only on the same tokens
            return (first.amount + second.amount).quantize(first.token.min_size)
        elif isinstance(first, TokenAmount) and not isinstance(second, TokenAmount):
            return (first.amount + Decimal(str(second))).quantize(first.token.min_size)
        elif not isinstance(first, TokenAmount) and isinstance(second, TokenAmount):
            return (Decimal(str(first)) + second.amount).quantize(second.token.min_size)
        else:
            print("SHOULD NOT HAPPEN")
            return Decimal(str(first)) + Decimal(str(second))

    @staticmethod
    def _safe_mul(first: Union[str, int, float, Decimal, "TokenAmount", PairSpotPrice],
                  second: Union[str, int, float, Decimal, "TokenAmount", PairSpotPrice]) -> Decimal:
        assert not (isinstance(first, TokenAmount) and isinstance(second, TokenAmount))
        assert not (isinstance(first, PairSpotPrice) and isinstance(second, PairSpotPrice))
        if isinstance(first, TokenAmount) and not isinstance(second, PairSpotPrice):
            return (first.amount * Decimal(str(second))).quantize(first.token.min_size)
        elif isinstance(first, TokenAmount) and isinstance(second, PairSpotPrice):
            exp = second.pair.quote.min_size if second.pair.base == first.token else second.pair.base.min_size
            return (first.amount * second.price).quantize(exp)
        elif not isinstance(first, PairSpotPrice) and isinstance(second, TokenAmount):
            return (Decimal(str(first)) * second.amount).quantize(second.token.min_size)
        elif isinstance(first, PairSpotPrice) and isinstance(second, TokenAmount):
            pass
        else:
            print("SHOULD NOT HAPPEN")

    def __add__(self, other: Union[str, int, float, Decimal, "TokenAmount"]) -> Decimal:
        return self._safe_add(self, other)

    def __radd__(self, other: Union[str, int, float, Decimal, "TokenAmount"]) -> Decimal:
        return self.__add__(other)

    def __sub__(self, other: Union[str, int, float, Decimal, "TokenAmount"]) -> Decimal:
        second = copy.deepcopy(other)
        if isinstance(other, TokenAmount):
            second.amount = -1 * other
        elif isinstance(other, str):
            second = Decimal("-1") * Decimal(other)
        else:
            second = -1 * other
        return self._safe_add(self, second)

    def __rsub__(self, other: Union[str, int, float, Decimal, "TokenAmount"]) -> Decimal:
        second = copy.deepcopy(self)
        if isinstance(self, TokenAmount):
            second.amount = -1 * self.amount
        return self._safe_add(other, second)

    def __mul__(self, other: Union[str, int, float, Decimal, PairSpotPrice]) -> Decimal:
        if isinstance(other, PairSpotPrice):
            assert self.token == other.pair.base  # 1[BTC] * 50[USD/BTC] = 50[USD]
        return self._safe_mul(self, other)

    def __rmul__(self, other: Union[Decimal, str, int, float, PairSpotPrice]) -> Decimal:
        return self.__mul__(other)

    def __truediv__(self, other: Union[Decimal, str, int, float, PairSpotPrice]) -> Decimal:
        second = copy.deepcopy(other)
        if isinstance(second, PairSpotPrice):
            assert self.token == other.pair.quote  # 100[USD] / 50[USD/BTC] = 2[BTC]
            second.price = other.price ** (-1)
        else:
            second = other ** (-1)
        return self._safe_mul(self, second)

    def __rtruediv__(self, other: Union[Decimal, str, int, float, PairSpotPrice]) -> Decimal:
        second = copy.deepcopy(self)
        if isinstance(self, TokenAmount):
            second.amount = self.amount ** (-1)
        if isinstance(other, PairSpotPrice):
            # TODO Non trovo il caso d'uso
            raise NotImplemented
        return self._safe_mul(other, second)
