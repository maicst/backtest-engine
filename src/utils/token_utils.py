import json

import requests

from src import settings
from src.models.token import Token, Pair
from src.utils.exception_utils import UnknownTokenException
from src.utils.singleton import Singleton


class PairFactory(metaclass=Singleton):
    def get_pair_by_name(self, base_name: str, quote_name) -> Pair:
        pair = Pair(get_token_info(base_name), get_token_info(quote_name))
        return pair


def clean_kraken_token_name(token: str) -> str:
    # Z = fiat, X = cryptocurrency
    if token[0] in ['Z', 'X'] and len(token) > 3:
        token = token[1:]
    return token


def get_token_info(token_name: str) -> Token:
    """
    Get token info from https://api.exchange.coinbase.com/
    """
    if settings.SHITTY_CONNECTION:
        with open(f'{settings.SRC_DIR}/../resources/token_info/{token_name}.json', 'r') as f:
            resp_json = json.load(f)
        return Token(name=resp_json["name"], symbol=resp_json["id"], min_size=resp_json["min_size"])
    token_info_url = f"https://api.exchange.coinbase.com/currencies/{token_name}"
    resp = requests.get(url=token_info_url)
    resp_json = resp.json()
    if resp.status_code == 200:
        return Token(name=resp_json["name"], symbol=resp_json["id"], min_size=resp_json["min_size"])
    else:
        raise UnknownTokenException(f"{token_name}: {resp_json['message']}")
