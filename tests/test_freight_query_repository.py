import unittest
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from application.dtos.freight_query import FreightQueryFilters
from application.exceptions import FreightPersistenceError
from domain.models.freight import FreightStatus
from infrastructure.persistence.sqlalchemy.freight_query_repository import (
    SqlAlchemyFreightQueryRepository,
)
from infrastructure.persistence.sqlalchemy.models import FreightModel


NOW = datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc)


class FakeResult:

    def __init__(self, rows):
        self._rows = list(rows)

    def mappings(self):
        return self

    def all(self):
        return list(self._rows)

    def one_or_none(self):
        if not self._rows:
            return None
        if len(self._rows) != 1:
            raise AssertionError("FakeResult recebeu mais de uma linha")
        return self._rows[0]


class FakeSession:

    def __init__(self, rows=(), error=None):
        self.rows = rows
        self.error = error
        self.statements = []

    def execute(self, statement):
        self.statements.append(statement)
        if self.error is not None:
            raise self.error
        return FakeResult(self.rows)


def make_row(**changes):
    row = {
        "freight_id": 77,
        "customer_id": 12,
        "customer_legal_name": "Empresa Historica Ltda",
        "customer_trade_name": "Historica",
        "customer_name": "Historica",
        "primary_quote_id": 21,
        "primary_quote_number": "ORC-2026-00021",
        "origin": "Curitiba/PR",
        "destination": "Sao Paulo/SP",
        "current_status": "COMPLETED",
        "contracted_revenue": Decimal("11200.00"),
        "approved_complementary_quote_count": 2,
        "financial_result_id": 8,
        "created_at": NOW,
        "started_at": NOW,
        "completed_at": NOW,
        "cancelled_at": None,
    }
    row.update(changes)
    return row


def compile_sql(statement) -> str:
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


class FreightQueryRepositoryTests(unittest.TestCase):

    def test_list_maps_projection_without_loading_aggregate(self):
        session = FakeSession(rows=(make_row(),))
        repository = SqlAlchemyFreightQueryRepository(session)

        result = repository.list(FreightQueryFilters())

        self.assertEqual(len(result), 1)
        item = result[0]
        self.assertEqual(item.freight_id, 77)
        self.assertEqual(item.customer_name, "Historica")
        self.assertEqual(item.origin, "Curitiba/PR")
        self.assertEqual(item.destination, "Sao Paulo/SP")
        self.assertEqual(item.current_status, FreightStatus.COMPLETED)
        self.assertEqual(item.contracted_revenue, Decimal("11200.00"))
        self.assertTrue(item.financially_closed)

        sql = compile_sql(session.statements[0])
        self.assertNotIn("freight_events", sql)
        self.assertNotIn("customers", sql)
        self.assertIn("primary_version", sql)
        self.assertIn("freight_financial_results", sql)

    def test_list_uses_historical_customer_snapshot(self):
        session = FakeSession(rows=(
            make_row(
                customer_legal_name="Razao Antiga SA",
                customer_trade_name=None,
                customer_name="Razao Antiga SA",
            ),
        ))
        repository = SqlAlchemyFreightQueryRepository(session)

        item = repository.list(FreightQueryFilters())[0]

        self.assertEqual(item.customer_name, "Razao Antiga SA")
        sql = compile_sql(session.statements[0])
        self.assertIn("customer_trade_name_snapshot", sql)
        self.assertIn("customer_legal_name_snapshot", sql)
        self.assertNotIn("JOIN customers", sql)

    def test_list_applies_customer_status_and_completion_filters(self):
        session = FakeSession()
        repository = SqlAlchemyFreightQueryRepository(session)
        completed_from = datetime(
            2026, 8, 1, tzinfo=timezone.utc
        )
        completed_to = datetime(
            2026, 8, 31, 23, 59, tzinfo=timezone.utc
        )

        repository.list(
            FreightQueryFilters(
                customer_id=12,
                status=FreightStatus.COMPLETED,
                completed_from=completed_from,
                completed_to=completed_to,
            )
        )

        sql = compile_sql(session.statements[0])
        self.assertIn("freights.customer_id = 12", sql)
        self.assertIn("freights.current_status = 'COMPLETED'", sql)
        self.assertIn("freights.completed_at >=", sql)
        self.assertIn("freights.completed_at <=", sql)
        self.assertIn("ORDER BY freights.created_at DESC", sql)

    def test_query_sums_all_approved_quotes_for_contracted_revenue(self):
        session = FakeSession()
        repository = SqlAlchemyFreightQueryRepository(session)

        repository.list(FreightQueryFilters())

        sql = compile_sql(session.statements[0])
        self.assertIn("sum(approved_version.contracted_price)", sql)
        self.assertIn("approved_quote.freight_id = freights.freight_id", sql)
        self.assertIn("approved_quote.current_status = 'APPROVED'", sql)

    def test_details_maps_complementaries_and_financial_result(self):
        session = FakeSession(rows=(make_row(),))
        repository = SqlAlchemyFreightQueryRepository(session)

        result = repository.get_by_id(77)

        self.assertIsNotNone(result)
        self.assertEqual(result.freight_id, 77)
        self.assertEqual(
            result.approved_complementary_quote_count,
            2,
        )
        self.assertTrue(result.financially_closed)
        self.assertEqual(result.financial_result_id, 8)
        self.assertEqual(
            result.customer_legal_name,
            "Empresa Historica Ltda",
        )
        self.assertEqual(result.customer_trade_name, "Historica")

    def test_details_returns_none_when_freight_does_not_exist(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession()
        )

        self.assertIsNone(repository.get_by_id(999))

    def test_missing_historical_route_is_reported_as_persistence_error(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession(rows=(make_row(origin=None),))
        )

        with self.assertRaisesRegex(
            FreightPersistenceError,
            "origem ausente",
        ):
            repository.list(FreightQueryFilters())

    def test_sqlalchemy_error_is_wrapped(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession(error=SQLAlchemyError("boom"))
        )

        with self.assertRaisesRegex(
            FreightPersistenceError,
            "lista de fretes",
        ):
            repository.list(FreightQueryFilters())

    def test_completed_at_index_is_declared_in_model(self):
        index_names = {
            index.name
            for index in FreightModel.__table__.indexes
        }
        self.assertIn(
            "ix_freights_completed_at",
            index_names,
        )


if __name__ == "__main__":
    unittest.main()
