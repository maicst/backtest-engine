from abc import ABC, abstractmethod
from typing import List

from src.connections.interface import ConnectorInterface
from src.models.order import Order
from src.models.user import AccountBalance


class MarketInterface(ABC):
    """ This class defines the market methods and converts inputs into the correct format for the market """
    connector: ConnectorInterface

    @abstractmethod
    def get_account_balance(self, **params) -> AccountBalance:
        raise NotImplementedError('not implemented')

    @abstractmethod
    def get_open_orders(self, **params) -> List[Order]:
        raise NotImplementedError('not implemented')

    @abstractmethod
    def get_orders_info(self, **params) -> List[Order]:
        raise NotImplementedError('not implemented')

    @abstractmethod
    def add_order(self, **params) -> Order:
        raise NotImplementedError('not implemented')

    def normalize_input_order(self, **params) -> Order:
        order: Order = params.pop('order')
        self.normalize_quantity(order=order, **params)
        return order

    @abstractmethod
    def normalize_quantity(self, **params):
        raise NotImplementedError('not implemented')
