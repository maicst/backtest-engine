import requests

from src.models.token import Pair, Token
from src.utils.exception_utils import UnknownTokenException
from src.utils.singleton import Singleton


class PairFactory(metaclass=Singleton):
    def get_pair_by_name(self, base_name: str, quote_name) -> Pair:
        pair = Pair(get_token_info(base_name), get_token_info(quote_name))
        return pair


def get_token_info(token_name: str) -> Token:
    """
    Get token info from https://api.exchange.coinbase.com/
    """
    token_info_url = f"https://api.exchange.coinbase.com/currencies/{token_name}"
    resp = requests.get(url=token_info_url)
    resp_json = resp.json()
    if resp.status_code == 200:
        return Token(name=resp_json["name"], symbol=resp_json["id"], min_size=resp_json["min_size"])
    else:
        raise UnknownTokenException(f"{token_name}: {resp_json['message']}")
