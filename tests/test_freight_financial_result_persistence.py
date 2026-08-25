import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from application.exceptions import (
    FreightFinancialResultPersistenceError
)
from domain.models.freight_financial_result import (
    FreightFinancialResult
)
from infrastructure.persistence.sqlalchemy.freight_financial_quote_repository import (
    SqlAlchemyFreightFinancialQuoteRepository
)
from infrastructure.persistence.sqlalchemy.freight_financial_result_repository import (
    SqlAlchemyFreightFinancialResultRepository
)
from infrastructure.persistence.sqlalchemy.freight_financial_result_unit_of_work import (
    SqlAlchemyFreightFinancialResultUnitOfWork
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightFinancialResultModel
)


NOW = datetime(
    2026,
    8,
    25,
    17,
    54,
    tzinfo=timezone.utc
)


def make_result() -> FreightFinancialResult:
    return FreightFinancialResult(
        freight_id=77,
        contracted_revenue=Decimal("10000.00"),
        actual_driver_amount=Decimal("3000.00"),
        toll_amount=Decimal("500.00"),
        actual_expenses_total=Decimal("250.00"),
        freight_insurance_total=Decimal("100.00"),
        tax_total=Decimal("1200.00"),
        administrative_cost_allocated=Decimal("400.00"),
        total_cost=Decimal("5450.00"),
        realized_result=Decimal("4550.00"),
        realized_margin=(
            Decimal("4550.00") / Decimal("5450.00")
        ),
        finalized_at=NOW
    )


class RecordingScalarSession:

    def __init__(self, scalar_result=None):
        self.scalar_result = scalar_result
        self.statement = None

    def scalar(self, statement):
        self.statement = statement
        return self.scalar_result


class EmptyScalarResult:

    def all(self):
        return []


class RecordingScalarsSession:

    def __init__(self):
        self.statement = None

    def scalars(self, statement):
        self.statement = statement
        return EmptyScalarResult()


class AddSession:

    def __init__(self):
        self.added = None
        self.flush_called = False

    def add(self, model):
        self.added = model

    def flush(self):
        self.flush_called = True
        self.added.freight_financial_result_id = 901


class UowSession:

    def __init__(self, fail_commit=False):
        self.fail_commit = fail_commit
        self.commit_called = False
        self.rollback_called = False
        self.close_called = False

    def commit(self):
        self.commit_called = True
        if self.fail_commit:
            raise SQLAlchemyError("falha simulada")

    def rollback(self):
        self.rollback_called = True

    def close(self):
        self.close_called = True


class FreightFinancialResultPersistenceTests(
    unittest.TestCase
):

    def test_model_has_expected_columns(self) -> None:
        table = FreightFinancialResultModel.__table__

        self.assertEqual(
            set(table.columns.keys()),
            {
                "freight_financial_result_id",
                "freight_id",
                "contracted_revenue",
                "actual_driver_amount",
                "toll_amount",
                "actual_expenses_total",
                "freight_insurance_total",
                "tax_total",
                "administrative_cost_allocated",
                "total_cost",
                "realized_result",
                "realized_margin",
                "finalized_at"
            }
        )
        self.assertTrue(
            table.c.realized_margin.nullable
        )
        self.assertFalse(
            table.c.finalized_at.nullable
        )

    def test_model_has_unique_freight_and_cascade_fk(self) -> None:
        table = FreightFinancialResultModel.__table__

        unique_names = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertIn(
            "uq_freight_financial_results_freight_id",
            unique_names
        )

        foreign_keys = list(
            table.c.freight_id.foreign_keys
        )
        self.assertEqual(len(foreign_keys), 1)
        self.assertEqual(
            foreign_keys[0].target_fullname,
            "freights.freight_id"
        )
        self.assertEqual(
            foreign_keys[0].ondelete,
            "CASCADE"
        )

    def test_model_has_financial_integrity_checks(self) -> None:
        table = FreightFinancialResultModel.__table__

        check_names = {
            constraint.name
            for constraint in table.constraints
            if isinstance(constraint, CheckConstraint)
        }

        self.assertIn(
            "ck_freight_financial_results_total_cost_consistent",
            check_names
        )
        self.assertIn(
            "ck_freight_financial_results_realized_result_consistent",
            check_names
        )
        self.assertIn(
            "ck_freight_financial_results_realized_margin_presence",
            check_names
        )
        self.assertEqual(len(check_names), 11)

    def test_repository_maps_domain_to_model(self) -> None:
        result = make_result()

        model = (
            SqlAlchemyFreightFinancialResultRepository
            ._to_model(result)
        )

        self.assertEqual(model.freight_id, 77)
        self.assertEqual(
            model.contracted_revenue,
            Decimal("10000.00")
        )
        self.assertEqual(
            model.realized_margin,
            result.realized_margin
        )
        self.assertEqual(model.finalized_at, NOW)

    def test_repository_maps_model_to_domain(self) -> None:
        source = make_result()
        model = (
            SqlAlchemyFreightFinancialResultRepository
            ._to_model(source)
        )
        model.freight_financial_result_id = 55

        restored = (
            SqlAlchemyFreightFinancialResultRepository
            ._to_domain(model)
        )

        self.assertEqual(
            restored.freight_financial_result_id,
            55
        )
        self.assertEqual(restored.freight_id, 77)
        self.assertEqual(
            restored.total_cost,
            source.total_cost
        )
        self.assertEqual(
            restored.realized_margin,
            source.realized_margin
        )

    def test_repository_add_flushes_and_returns_persisted_id(self) -> None:
        session = AddSession()
        repository = (
            SqlAlchemyFreightFinancialResultRepository(
                session
            )
        )

        created = repository.add(
            make_result()
        )

        self.assertTrue(session.flush_called)
        self.assertIsNotNone(session.added)
        self.assertEqual(
            created.freight_financial_result_id,
            901
        )

    def test_repository_get_by_freight_id_returns_none(self) -> None:
        session = RecordingScalarSession()
        repository = (
            SqlAlchemyFreightFinancialResultRepository(
                session
            )
        )

        result = repository.get_by_freight_id(77)

        self.assertIsNone(result)
        sql = str(
            session.statement.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True}
            )
        )
        self.assertIn(
            "freight_financial_results.freight_id = 77",
            sql
        )

    def test_financial_quote_repository_filters_and_locks(self) -> None:
        session = RecordingScalarsSession()
        repository = (
            SqlAlchemyFreightFinancialQuoteRepository(
                session
            )
        )

        result = repository.list_by_freight_id_for_update(
            77
        )

        self.assertEqual(result, ())
        sql = str(
            session.statement.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True}
            )
        )
        self.assertIn("quotes.freight_id = 77", sql)
        self.assertIn("ORDER BY quotes.quote_id", sql)
        self.assertIn("FOR UPDATE", sql)

    def test_uow_uses_same_session_for_all_repositories(self) -> None:
        session = UowSession()
        unit_of_work = (
            SqlAlchemyFreightFinancialResultUnitOfWork(
                lambda: session
            )
        )

        with unit_of_work as opened:
            self.assertIs(
                opened.freights._session,
                session
            )
            self.assertIs(
                opened.quotes._session,
                session
            )
            self.assertIs(
                opened.driver_assignments._session,
                session
            )
            self.assertIs(
                opened.expenses._session,
                session
            )
            self.assertIs(
                opened.financial_results._session,
                session
            )

        self.assertTrue(session.close_called)

    def test_uow_commit_wraps_sqlalchemy_error(self) -> None:
        session = UowSession(
            fail_commit=True
        )
        unit_of_work = (
            SqlAlchemyFreightFinancialResultUnitOfWork(
                lambda: session
            )
        )

        with unit_of_work:
            with self.assertRaises(
                FreightFinancialResultPersistenceError
            ):
                unit_of_work.commit()

        self.assertTrue(session.rollback_called)

    def test_migration_extends_current_e10_head(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        migration_path = (
            project_root
            / "alembic"
            / "versions"
            / (
                "c7a1e5d9f2b4_"
                "adiciona_fechamento_financeiro_do_frete.py"
            )
        )

        source = migration_path.read_text(
            encoding="utf-8"
        )

        self.assertIn(
            'revision: str = "c7a1e5d9f2b4"',
            source
        )
        self.assertIn(
            'down_revision: Union[str, Sequence[str], None] = "5f2a7c8d1e64"',
            source
        )
        self.assertIn(
            '"freight_financial_results"',
            source
        )


if __name__ == "__main__":
    unittest.main()
