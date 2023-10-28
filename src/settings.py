import os
from datetime import datetime
from decimal import Decimal
from distutils.util import strtobool

from dotenv import load_dotenv

from src.utils import token_utils

load_dotenv()

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
SHITTY_CONNECTION = bool(strtobool(os.getenv('SHITTY_CONNECTION', "False")))
DEBUG = bool(strtobool(os.getenv('DEBUG', "True")))
BIG_BANG_DATE = datetime(2017, 1, 1)

# TODO mettere in env
MONGO_URL = os.getenv('MONGO_URL')

KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY')
KRAKEN_API_SECRET = os.getenv('KRAKEN_API_SECRET')
KRAKEN_BASE_URL = os.getenv('KRAKEN_BASE_URL', "https://api.kraken.com")

MOCK_MARKET_FEE = Decimal("0.24")  # percentage

DEFAULT_MOCK_BALANCE = {
    "BTC": "0.1",
    "USD": "1000",
}
MOCK_BALANCE_CONFIG_FILE = os.getenv('MOCK_BALANCE_CONFIG_FILE', f"{SRC_DIR}/../config/balance.json")
KRAKEN_TOKEN_INFO_FILE = os.getenv('KRAKEN_TOKEN_INFO_FILE', f"{SRC_DIR}/../config/kraken_assets.json")

NEGATIVE_BALANCE_AMOUNT = bool(strtobool(os.getenv('NEGATIVE_BALANCE_AMOUNT', "True")))
ACCOUNT_BALANCE_CURRENCY = "USD"
ACCOUNT_BALANCE_CURRENCY_TOKEN_INFO = token_utils.get_token_info(ACCOUNT_BALANCE_CURRENCY)

USE_DYNAMO = False
