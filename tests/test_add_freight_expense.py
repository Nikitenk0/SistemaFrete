import unittest
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError
)
from application.use_cases.add_freight_expense import AddFreightExpense
from domain.models.freight_expense import (
    FreightExpense,
    FreightExpenseType
)


NOW = datetime(2026, 8, 25, 16, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class FakeFreight:
    freight_id: int
    current_status: str


class FakeFreightRepository:

    def __init__(self, freight: FakeFreight | None):
        self.freight = freight
        self.locked_id: int | None = None

    def get_by_id_for_update(self, freight_id: int):
        self.locked_id = freight_id
        if self.freight and self.freight.freight_id == freight_id:
            return self.freight
        return None


class FakeFreightExpenseRepository:

    def __init__(self):
        self.added: FreightExpense | None = None

    def add(self, expense: FreightExpense) -> FreightExpense:
        self.added = expense
        return replace(expense, freight_expense_id=501)


class FakeUnitOfWork:

    def __init__(self, freight: FakeFreight | None):
        self.freights = FakeFreightRepository(freight)
        self.expenses = FakeFreightExpenseRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


class FakeFactory:

    def __init__(self, freight: FakeFreight | None):
        self.freight = freight
        self.created: list[FakeUnitOfWork] = []

    def create(self) -> FakeUnitOfWork:
        unit_of_work = FakeUnitOfWork(self.freight)
        self.created.append(unit_of_work)
        return unit_of_work


def execute_default(
    factory: FakeFactory,
    **overrides
) -> FreightExpense:
    params = {
        "freight_id": 10,
        "expense_type": FreightExpenseType.MUNCK,
        "value": Decimal("850.00"),
        "occurred_at": NOW,
        "observation": "Descarga no cliente",
        "created_by": 7,
    }
    params.update(overrides)
    return AddFreightExpense(factory).execute(**params)


class AddFreightExpenseTests(unittest.TestCase):

    def test_adds_expense_and_commits(self) -> None:
        factory = FakeFactory(FakeFreight(10, "IN_PROGRESS"))
        result = execute_default(factory)

        unit_of_work = factory.created[-1]
        self.assertEqual(result.freight_expense_id, 501)
        self.assertEqual(unit_of_work.freights.locked_id, 10)
        self.assertTrue(unit_of_work.committed)
        self.assertTrue(unit_of_work.expenses.added.is_considered)
        self.assertIsNotNone(unit_of_work.expenses.added.created_at)

    def test_allows_expense_in_all_current_freight_statuses(self) -> None:
        for status in (
            "PENDING",
            "IN_PROGRESS",
            "COMPLETED",
            "CANCELLED",
        ):
            with self.subTest(status=status):
                factory = FakeFactory(FakeFreight(10, status))
                result = execute_default(factory)
                self.assertEqual(result.freight_expense_id, 501)
                self.assertTrue(factory.created[-1].committed)

    def test_adds_outros_with_description(self) -> None:
        factory = FakeFactory(FakeFreight(10, "COMPLETED"))
        result = execute_default(
            factory,
            expense_type=FreightExpenseType.OUTROS,
            custom_description="Taxa de estacionamento",
            value=Decimal("90.00")
        )
        self.assertEqual(result.custom_description, "Taxa de estacionamento")

    def test_rejects_outros_without_description(self) -> None:
        factory = FakeFactory(FakeFreight(10, "IN_PROGRESS"))
        with self.assertRaises(InvalidFreightDataError):
            execute_default(
                factory,
                expense_type=FreightExpenseType.OUTROS,
                custom_description=None
            )
        self.assertFalse(factory.created[-1].committed)

    def test_rejects_non_positive_value(self) -> None:
        factory = FakeFactory(FakeFreight(10, "IN_PROGRESS"))
        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "maior que zero"
        ):
            execute_default(factory, value=Decimal("0"))
        self.assertFalse(factory.created[-1].committed)

    def test_rejects_missing_freight(self) -> None:
        factory = FakeFactory(None)
        with self.assertRaises(FreightNotFoundError):
            execute_default(factory)
        self.assertFalse(factory.created[-1].committed)

    def test_rejects_invalid_freight_id_before_uow(self) -> None:
        factory = FakeFactory(FakeFreight(10, "PENDING"))
        with self.assertRaisesRegex(InvalidFreightDataError, "freight_id"):
            execute_default(factory, freight_id=0)
        self.assertEqual(factory.created, [])

    def test_rejects_invalid_created_by_before_uow(self) -> None:
        factory = FakeFactory(FakeFreight(10, "PENDING"))
        with self.assertRaisesRegex(InvalidFreightDataError, "created_by"):
            execute_default(factory, created_by=0)
        self.assertEqual(factory.created, [])


if __name__ == "__main__":
    unittest.main()
