from typing import Protocol

from domain.models.freight_expense import FreightExpense


class FreightExpenseRepository(Protocol):

    def add(
        self,
        expense: FreightExpense
    ) -> FreightExpense:
        ...

    def save(
        self,
        expense: FreightExpense
    ) -> FreightExpense:
        ...

    def get_by_id(
        self,
        freight_expense_id: int
    ) -> FreightExpense | None:
        ...

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightExpense, ...]:
        ...
