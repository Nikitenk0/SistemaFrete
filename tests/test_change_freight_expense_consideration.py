import unittest
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from application.exceptions import (
    FreightExpenseNotFoundError,
    FreightNotFoundError,
    InvalidFreightDataError
)
from application.use_cases.change_freight_expense_consideration import (
    ChangeFreightExpenseConsideration
)
from domain.models.freight_expense import (
    FreightExpense,
    FreightExpenseType
)


NOW = datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc)


class FakeFreight:
    def __init__(self, freight_id: int):
        self.freight_id = freight_id


class FakeFreightRepository:
    def __init__(self, freight):
        self.freight = freight
        self.locked_id = None

    def get_by_id_for_update(self, freight_id: int):
        self.locked_id = freight_id
        if self.freight and self.freight.freight_id == freight_id:
            return self.freight
        return None


class FakeExpenseRepository:
    def __init__(self, expense):
        self.expense = expense
        self.saved = None

    def get_by_id(self, expense_id: int):
        if (
            self.expense is not None
            and self.expense.freight_expense_id == expense_id
        ):
            return self.expense
        return None

    def save(self, expense: FreightExpense):
        self.saved = expense
        self.expense = expense
        return expense


class FakeUnitOfWork:
    def __init__(self, freight, expense):
        self.freights = FakeFreightRepository(freight)
        self.expenses = FakeExpenseRepository(expense)
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeFactory:
    def __init__(self, freight, expense):
        self.freight = freight
        self.expense = expense
        self.created = []

    def create(self):
        uow = FakeUnitOfWork(self.freight, self.expense)
        self.created.append(uow)
        return uow


def make_expense(
    *,
    freight_id: int = 10,
    is_considered: bool = True
) -> FreightExpense:
    return FreightExpense(
        freight_expense_id=501,
        freight_id=freight_id,
        expense_type=FreightExpenseType.MUNCK,
        value=Decimal("850.00"),
        occurred_at=NOW,
        observation="Descarga",
        is_considered=is_considered,
        created_at=NOW,
        created_by=7
    )


class ChangeFreightExpenseConsiderationTests(unittest.TestCase):

    def test_disconsiders_expense_and_commits(self):
        factory = FakeFactory(
            FakeFreight(10),
            make_expense()
        )

        result = ChangeFreightExpenseConsideration(
            factory
        ).execute(10, 501, False)

        uow = factory.created[-1]
        self.assertFalse(result.is_considered)
        self.assertEqual(uow.freights.locked_id, 10)
        self.assertIsNotNone(uow.expenses.saved)
        self.assertTrue(uow.committed)

    def test_reconsiders_expense_and_commits(self):
        factory = FakeFactory(
            FakeFreight(10),
            make_expense(is_considered=False)
        )

        result = ChangeFreightExpenseConsideration(
            factory
        ).execute(10, 501, True)

        self.assertTrue(result.is_considered)
        self.assertTrue(factory.created[-1].committed)

    def test_is_idempotent_when_state_is_already_requested(self):
        expense = make_expense(is_considered=False)
        factory = FakeFactory(FakeFreight(10), expense)

        result = ChangeFreightExpenseConsideration(
            factory
        ).execute(10, 501, False)

        uow = factory.created[-1]
        self.assertIs(result, expense)
        self.assertIsNone(uow.expenses.saved)
        self.assertFalse(uow.committed)

    def test_rejects_missing_freight(self):
        factory = FakeFactory(None, make_expense())

        with self.assertRaises(FreightNotFoundError):
            ChangeFreightExpenseConsideration(
                factory
            ).execute(10, 501, False)

        self.assertFalse(factory.created[-1].committed)

    def test_rejects_missing_expense(self):
        factory = FakeFactory(FakeFreight(10), None)

        with self.assertRaises(FreightExpenseNotFoundError):
            ChangeFreightExpenseConsideration(
                factory
            ).execute(10, 501, False)

        self.assertFalse(factory.created[-1].committed)

    def test_rejects_expense_from_another_freight(self):
        factory = FakeFactory(
            FakeFreight(10),
            make_expense(freight_id=11)
        )

        with self.assertRaises(FreightExpenseNotFoundError):
            ChangeFreightExpenseConsideration(
                factory
            ).execute(10, 501, False)

        self.assertFalse(factory.created[-1].committed)

    def test_rejects_invalid_arguments_before_uow(self):
        factory = FakeFactory(FakeFreight(10), make_expense())
        use_case = ChangeFreightExpenseConsideration(factory)

        for kwargs in (
            {"freight_id": 0, "freight_expense_id": 501, "is_considered": False},
            {"freight_id": 10, "freight_expense_id": 0, "is_considered": False},
            {"freight_id": 10, "freight_expense_id": 501, "is_considered": 1},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(InvalidFreightDataError):
                    use_case.execute(**kwargs)

        self.assertEqual(factory.created, [])


if __name__ == "__main__":
    unittest.main()
