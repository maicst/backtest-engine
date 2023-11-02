from decimal import Decimal

import pytest

from src.models.token import Pair, PairSpotPrice, Token, TokenAmount
from src.utils import token_utils
from src.utils.exception_utils import TokenArithmeticsException


@pytest.fixture
def token_btc() -> Token:
    return token_utils.get_token_info("BTC")


@pytest.fixture
def token_usd() -> Token:
    return token_utils.get_token_info("USD")


def test_create_new_token_amount(token_btc):
    token_amount = TokenAmount(token_btc, 100)
    assert Decimal("100") == token_amount.amount


def test_token_amount_decimals(token_usd):
    token_amount = TokenAmount(token_usd, 100)
    assert token_amount.token.min_size == Decimal(str(10 ** token_amount.amount.as_tuple().exponent))


@pytest.mark.sum
def test_token_amount_plus_number(token_usd):
    token_amount = TokenAmount(token_usd, 33.3333333)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = token_amount + "2.105"  # round up
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.sum
def test_number_plus_token_amount(token_usd):
    token_amount = TokenAmount(token_usd, 33.3333333)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = 2.104 + token_amount
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.sum
def test_token_amount_plus_token_amount(token_usd):
    token_amount_1 = TokenAmount(token_usd, 33.3333333)
    token_amount_2 = TokenAmount(token_usd, 33.3333333)
    res_1 = token_amount_1 + token_amount_2
    res_2 = token_amount_2 + token_amount_1
    assert TokenAmount(token_usd, Decimal("66.66")) == res_1
    assert res_1 == res_2


@pytest.mark.sum
def test_token_amount_plus_token_amount_exception(token_usd, token_btc):
    token_amount_1 = TokenAmount(token_usd, 33.3333333)
    token_amount_2 = TokenAmount(token_btc, 1.1)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = token_amount_1 + token_amount_2
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.sub
def test_token_amount_minus_number(token_usd):
    token_amount = TokenAmount(token_usd, 33.3333333)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = token_amount - "3.33"  # round down
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.sub
def test_number_minus_token_amount(token_usd):
    token_amount = TokenAmount(token_usd, 3.3333333)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = "33.3" - token_amount
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.sub
def test_token_amount_minus_token_amount(token_usd):
    token_amount_1 = TokenAmount(token_usd, 33.3333333)
    token_amount_2 = TokenAmount(token_usd, 1.1)
    res = token_amount_1 - token_amount_2
    assert TokenAmount(token_usd, Decimal("32.23")) == res


@pytest.mark.sub
def test_token_amount_minus_token_amount_exception(token_usd, token_btc):
    token_amount_1 = TokenAmount(token_usd, 33.3333333)
    token_amount_2 = TokenAmount(token_btc, 1.1)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = token_amount_1 + token_amount_2
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.mul
def test_token_amount_x_number(token_usd):
    token_amount = TokenAmount(token_usd, 33.3333333)
    three_times = token_amount * Decimal("3")
    assert TokenAmount(token_usd, Decimal("99.99")) == three_times


@pytest.mark.mul
def test_token_amount_x_token_amount(token_usd):
    token_amount_1 = TokenAmount(token_usd, 1.2345)
    token_amount_2 = TokenAmount(token_usd, 2.123456789)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = token_amount_1 * token_amount_2
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.mul
def test_token_amount_x_price(token_usd, token_btc):
    token_amount = TokenAmount(token_btc, 1)
    pair = Pair(token_btc, token_usd)
    price = PairSpotPrice(pair=pair, price=123.456)
    res = token_amount * price  # BTC * USD/BTC = USD
    assert TokenAmount(token_usd, Decimal("123.46")) == res


@pytest.mark.div
def test_token_amount_div_number(token_usd):
    token_amount = TokenAmount(token_usd, 100)
    one_third = token_amount / 3
    assert TokenAmount(token_usd, Decimal("33.33")) == one_third


@pytest.mark.div
def test_token_amount_div_token_amount(token_usd):
    token_amount_1 = TokenAmount(token_usd, 100)
    token_amount_2 = TokenAmount(token_usd, 3)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = token_amount_1 / token_amount_2
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.div
def test_number_div_token_amount(token_usd):
    token_amount = TokenAmount(token_usd, 100)
    with pytest.raises(TokenArithmeticsException) as exc:
        res = 3 / token_amount
    assert type(exc.value) == TokenArithmeticsException


@pytest.mark.div
def test_token_amount_div_price(token_usd, token_btc):
    # Fallisce perchè il calcolo è fatto con 8 decimali e nella divisione si perde precisione
    token_amount = TokenAmount(token_usd, 100000) # 1 precision loss foreach 0
    pair = Pair(token_btc, token_usd)
    price = PairSpotPrice(pair=pair, price=30000)
    res = token_amount / price  # USD / (USD/BTC) = BTC
    assert TokenAmount(token_btc, Decimal("3.33333333")) == res
