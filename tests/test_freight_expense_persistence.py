import unittest
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint

from application.exceptions import FreightExpenseNotFoundError
from domain.models.freight_expense import (
    FreightExpense,
    FreightExpenseType
)
from infrastructure.persistence.sqlalchemy.base import Base
import infrastructure.persistence.sqlalchemy.models  # noqa: F401
from infrastructure.persistence.sqlalchemy.freight_expense_repository import (
    SqlAlchemyFreightExpenseRepository
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightExpenseModel
)


NOW = datetime(
    2026,
    8,
    25,
    17,
    0,
    tzinfo=timezone.utc
)


class FreightExpenseMetadataTests(unittest.TestCase):

    def test_registers_freight_expenses_table(self) -> None:
        table = Base.metadata.tables["freight_expenses"]

        expected_columns = {
            "freight_expense_id",
            "freight_id",
            "expense_type",
            "custom_description",
            "value",
            "occurred_at",
            "observation",
            "is_considered",
            "created_at",
            "created_by"
        }

        self.assertEqual(
            set(table.c.keys()),
            expected_columns
        )
        self.assertFalse(table.c.freight_id.nullable)
        self.assertFalse(table.c.value.nullable)
        self.assertFalse(table.c.occurred_at.nullable)
        self.assertFalse(table.c.is_considered.nullable)

    def test_registers_expected_check_constraints(self) -> None:
        table = Base.metadata.tables["freight_expenses"]
        names = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }

        self.assertIn(
            "ck_freight_expenses_expense_type",
            names
        )
        self.assertIn(
            "ck_freight_expenses_value_positive",
            names
        )
        self.assertIn(
            "ck_freight_expenses_custom_description_by_type",
            names
        )

    def test_registers_expected_foreign_key_delete_rules(self) -> None:
        table = Base.metadata.tables["freight_expenses"]

        freight_fk = next(
            iter(table.c.freight_id.foreign_keys)
        )
        created_by_fk = next(
            iter(table.c.created_by.foreign_keys)
        )

        self.assertEqual(
            freight_fk.target_fullname,
            "freights.freight_id"
        )
        self.assertEqual(freight_fk.ondelete, "CASCADE")
        self.assertEqual(
            created_by_fk.target_fullname,
            "users.user_id"
        )
        self.assertEqual(created_by_fk.ondelete, "SET NULL")

    def test_is_considered_has_database_default_true(self) -> None:
        table = Base.metadata.tables["freight_expenses"]
        self.assertIsNotNone(
            table.c.is_considered.server_default
        )


class FreightExpenseMappingTests(unittest.TestCase):

    def test_maps_domain_expense_to_model(self) -> None:
        expense = FreightExpense(
            freight_id=7,
            expense_type=FreightExpenseType.MUNCK,
            value=Decimal("850.00"),
            occurred_at=NOW,
            observation="Descarga no cliente",
            created_at=NOW,
            created_by=3
        )

        model = (
            SqlAlchemyFreightExpenseRepository
            ._to_model(expense)
        )

        self.assertEqual(model.freight_id, 7)
        self.assertEqual(model.expense_type, "MUNCK")
        self.assertEqual(model.value, Decimal("850.00"))
        self.assertTrue(model.is_considered)
        self.assertIsNone(model.custom_description)
        self.assertEqual(model.created_by, 3)

    def test_maps_persisted_expense_to_domain(self) -> None:
        model = FreightExpenseModel(
            freight_expense_id=11,
            freight_id=7,
            expense_type="OUTROS",
            custom_description="Taxa de estacionamento",
            value=Decimal("90.00"),
            occurred_at=NOW,
            observation=None,
            is_considered=False,
            created_at=NOW,
            created_by=None
        )

        expense = (
            SqlAlchemyFreightExpenseRepository
            ._to_domain(model)
        )

        self.assertEqual(expense.freight_expense_id, 11)
        self.assertEqual(
            expense.expense_type,
            FreightExpenseType.OUTROS
        )
        self.assertEqual(
            expense.custom_description,
            "Taxa de estacionamento"
        )
        self.assertEqual(expense.value, Decimal("90.00"))
        self.assertFalse(expense.is_considered)


class FakeScalarSession:

    def __init__(self):
        self.statement = None

    def scalar(self, statement):
        self.statement = statement
        return None


class FakeScalarsResult:

    def all(self):
        return []


class FakeScalarsSession:

    def __init__(self):
        self.statement = None

    def scalars(self, statement):
        self.statement = statement
        return FakeScalarsResult()


class FreightExpenseRepositoryQueryTests(unittest.TestCase):

    def test_get_by_id_returns_none_when_not_found(self) -> None:
        session = FakeScalarSession()
        repository = SqlAlchemyFreightExpenseRepository(
            session
        )

        result = repository.get_by_id(99)

        self.assertIsNone(result)
        self.assertIsNotNone(session.statement)

    def test_list_by_freight_id_returns_tuple(self) -> None:
        session = FakeScalarsSession()
        repository = SqlAlchemyFreightExpenseRepository(
            session
        )

        result = repository.list_by_freight_id(7)

        self.assertEqual(result, ())
        self.assertIsNotNone(session.statement)


class FakeSaveSession:

    def __init__(self, model):
        self.model = model
        self.statement = None
        self.flushed = False

    def scalar(self, statement):
        self.statement = statement
        return self.model

    def flush(self):
        self.flushed = True


class FreightExpenseRepositorySaveTests(unittest.TestCase):

    def test_save_updates_only_is_considered(self) -> None:
        model = FreightExpenseModel(
            freight_expense_id=11,
            freight_id=7,
            expense_type="MUNCK",
            custom_description=None,
            value=Decimal("850.00"),
            occurred_at=NOW,
            observation="Descarga",
            is_considered=True,
            created_at=NOW,
            created_by=3
        )
        session = FakeSaveSession(model)
        repository = SqlAlchemyFreightExpenseRepository(session)

        expense = FreightExpense(
            freight_expense_id=11,
            freight_id=7,
            expense_type=FreightExpenseType.MUNCK,
            value=Decimal("850.00"),
            occurred_at=NOW,
            observation="Descarga",
            is_considered=False,
            created_at=NOW,
            created_by=3
        )

        result = repository.save(expense)

        self.assertFalse(model.is_considered)
        self.assertFalse(result.is_considered)
        self.assertTrue(session.flushed)

    def test_save_rejects_missing_id(self) -> None:
        repository = SqlAlchemyFreightExpenseRepository(
            FakeSaveSession(None)
        )
        expense = FreightExpense(
            freight_id=7,
            expense_type=FreightExpenseType.MUNCK,
            value=Decimal("850.00"),
            occurred_at=NOW
        )

        with self.assertRaisesRegex(ValueError, "não possui id"):
            repository.save(expense)

    def test_save_rejects_missing_persisted_expense(self) -> None:
        repository = SqlAlchemyFreightExpenseRepository(
            FakeSaveSession(None)
        )
        expense = FreightExpense(
            freight_expense_id=11,
            freight_id=7,
            expense_type=FreightExpenseType.MUNCK,
            value=Decimal("850.00"),
            occurred_at=NOW,
            created_at=NOW
        )

        with self.assertRaises(FreightExpenseNotFoundError):
            repository.save(expense)

    def test_save_rejects_changes_to_origin_fields(self) -> None:
        model = FreightExpenseModel(
            freight_expense_id=11,
            freight_id=7,
            expense_type="MUNCK",
            custom_description=None,
            value=Decimal("850.00"),
            occurred_at=NOW,
            observation=None,
            is_considered=True,
            created_at=NOW,
            created_by=None
        )
        repository = SqlAlchemyFreightExpenseRepository(
            FakeSaveSession(model)
        )
        changed = FreightExpense(
            freight_expense_id=11,
            freight_id=7,
            expense_type=FreightExpenseType.MUNCK,
            value=Decimal("900.00"),
            occurred_at=NOW,
            is_considered=False,
            created_at=NOW
        )

        with self.assertRaisesRegex(ValueError, "imutáveis"):
            repository.save(changed)


if __name__ == "__main__":
    unittest.main()
