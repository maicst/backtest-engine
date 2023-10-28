from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from src import settings
from src.models.token import TokenAmount
from src.models.user import AccountBalance
from src.utils.exception_utils import NotEnoughMoneyException


class MockAccountBalance(AccountBalance):
    update_date: datetime

    def __init__(self, balance):
        super().__init__(balance)
        self.update_date = datetime.utcnow()

    def update_balance(self, token_symbol: str, amount: Union[int, float, str, Decimal], execution_date: datetime):
        token_amount: Optional[TokenAmount] = self.get_token_amount_by_symbol(token_symbol)
        if not token_amount:
            raise NotEnoughMoneyException()

        if settings.NEGATIVE_BALANCE_AMOUNT or token_amount + amount >= 0:
            token_amount.amount += amount
            self.update_date = execution_date
        else:
            raise NotEnoughMoneyException()
