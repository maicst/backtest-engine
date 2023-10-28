from abc import ABC, abstractmethod


class ConnectorInterface(ABC):
    """ This class only query the market """

    @abstractmethod
    def get_account_balance(self, **params):
        raise NotImplementedError('not implemented')

    @abstractmethod
    def get_open_orders(self, **params):
        raise NotImplementedError('not implemented')

    @abstractmethod
    def get_orders_info(self, **params):
        raise NotImplementedError('not implemented')

    @abstractmethod
    def add_order(self, **params):
        raise NotImplementedError('not implemented')

    @abstractmethod
    def get_instant_price(self, **params):
        raise NotImplementedError('not implemented')
