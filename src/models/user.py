from decimal import Decimal
from typing import List, Optional

from src.models.token import TokenAmount


class AccountBalance:
    """
    AccountBalance = Portfolio
    """
    balance: List[TokenAmount]
    fees: List[TokenAmount]
    value: Decimal

    def __init__(self, balance):
        self.balance = balance
        self.fees = []

    def get_token_amount_by_symbol(self, symbol: str) -> Optional[TokenAmount]:
        return next((t for t in self.balance if t.token.symbol == symbol), None)

    def __iter__(self):
        yield "value", self.value
        for b in self.balance:
            yield b.token.symbol, b.amount
