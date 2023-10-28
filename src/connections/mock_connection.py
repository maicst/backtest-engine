from typing import List

from src.connections.interface import ConnectorInterface
from src.models.order import Order
from src.models.token import PairSpotPrice
from src.models.user import AccountBalance
from src.services.mock_service import MockService


class MockConnector(ConnectorInterface):
    service: MockService

    def __init__(self, initial_balance: dict = None):
        self.service = MockService(initial_balance)

    def get_account_balance(self, **params) -> AccountBalance:
        return self.service.get_account_balance(execution_date=params.get('execution_date'))

    def get_open_orders(self, **params) -> List[Order]:
        return self.service.get_open_orders(**params)

    def get_orders_info(self, **params) -> List[Order]:
        return self.service.get_orders_info(**params)

    def add_order(self, **params):
        return self.service.add_order(**params)

    def get_instant_price(self, **params) -> PairSpotPrice:
        return self.service.get_instant_price(**params)
