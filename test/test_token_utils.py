import pytest

from src.models.token import Token
from src.utils import token_utils
from src.utils.exception_utils import UnknownTokenException


def test_get_token_info():
    token: Token = token_utils.get_token_info("BTC")
    assert "Bitcoin" == token.name


def test_get_token_info_exception():
    with pytest.raises(UnknownTokenException) as exc:
        token_utils.get_token_info("BROKEN")
    assert type(exc.value) == UnknownTokenException


def test_pair_factory():
    factory = token_utils.PairFactory()
    pair = factory.get_pair_by_name(base_name="BTC", quote_name="USD")
    assert pair.base.name == 'Bitcoin' and pair.quote.name == 'United States Dollar'
