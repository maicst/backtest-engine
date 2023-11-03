from decimal import Decimal

import pytest

from src.models.token import Pair, PairSpotPrice, Token
from src.utils import token_utils
from src.utils.exception_utils import TokenArithmeticException


@pytest.fixture
def token_btc() -> Token:
    return token_utils.get_token_info("BTC")


@pytest.fixture
def token_usd() -> Token:
    return token_utils.get_token_info("USD")


@pytest.fixture
def pair_btcusd(token_btc, token_usd) -> Pair:
    return Pair(token_btc, token_usd)


def test_create_new_spot_price(pair_btcusd):
    spot_price = PairSpotPrice(pair=pair_btcusd, price=100)
    assert "1 BTC = 100.00 USD" == str(spot_price)


def test_inverse_spot_price(pair_btcusd):
    spot_price = PairSpotPrice(pair=pair_btcusd, price=100)
    assert Decimal("0.01") == spot_price.inverse_price


@pytest.mark.sum
def test_spot_price_plus_spot_price(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    spot_price_2 = PairSpotPrice(pair=pair_btcusd, price=20)
    res = spot_price_1 + spot_price_2
    assert PairSpotPrice(pair=pair_btcusd, price=Decimal("120")) == res


@pytest.mark.sum
def test_spot_price_plus_number(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    with pytest.raises(TokenArithmeticException) as exc:
        res = spot_price_1 + Decimal("20")
    assert type(exc.value) == TokenArithmeticException


@pytest.mark.sub
def test_spot_price_minus_spot_price(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    spot_price_2 = PairSpotPrice(pair=pair_btcusd, price=20)
    res = spot_price_1 - spot_price_2
    assert PairSpotPrice(pair=pair_btcusd, price=Decimal("80")) == res


@pytest.mark.sub
def test_spot_price_minus_number(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    with pytest.raises(TokenArithmeticException) as exc:
        res = spot_price_1 - Decimal("20")
    assert type(exc.value) == TokenArithmeticException


@pytest.mark.mul
def test_spot_price_x_number(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    res = spot_price_1 * 3
    assert PairSpotPrice(pair=pair_btcusd, price=Decimal("300")) == res
    res = -1 * spot_price_1
    assert PairSpotPrice(pair=pair_btcusd, price=Decimal("-100")) == res


@pytest.mark.mul
def test_spot_price_div_number(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    res = spot_price_1 / 3
    assert PairSpotPrice(pair=pair_btcusd, price=Decimal("33.33")) == res


@pytest.mark.mul
def test_spot_price_div_spot_price(pair_btcusd):
    spot_price_1 = PairSpotPrice(pair=pair_btcusd, price=100)
    spot_price_2 = PairSpotPrice(pair=pair_btcusd, price=80)
    res = spot_price_2 / spot_price_1
    assert Decimal("0.80") == res
