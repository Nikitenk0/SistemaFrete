import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from application.dtos.freight_query import FreightQueryFilters
from application.exceptions import FreightPersistenceError
from domain.models.freight import FreightStatus
from domain.models.freight_event import FreightEventType
from domain.models.freight_expense import FreightExpenseType
from domain.models.freight_vehicle_record import FreightVehicleType
from infrastructure.persistence.sqlalchemy.freight_query_repository import (
    SqlAlchemyFreightQueryRepository,
)
from infrastructure.persistence.sqlalchemy.models import FreightModel


NOW = datetime(2026, 8, 25, 18, 0, tzinfo=timezone.utc)
LATER = NOW + timedelta(hours=4)


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

    def __init__(self, batches=()):
        self._batches = list(batches)
        self.statements = []

    def execute(self, statement):
        self.statements.append(statement)

        if not self._batches:
            return FakeResult(())

        batch = self._batches.pop(0)
        if isinstance(batch, Exception):
            raise batch

        return FakeResult(batch)


def make_base_row(**changes):
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
        "completed_at": LATER,
        "cancelled_at": None,
    }
    row.update(changes)
    return row


def make_unit_row(**changes):
    row = {
        "freight_transport_unit_id": 101,
        "position": 1,
        "freight_vehicle_record_id": 301,
        "vehicle_type": "CARRETA_LS",
        "plate": "ABC1D23",
        "axle_count": 6,
        "pallet_capacity_min": 28,
        "pallet_capacity_max": 28,
        "payload_capacity_kg": 30000,
    }
    row.update(changes)
    return row


def make_assignment_row(**changes):
    row = {
        "freight_driver_assignment_id": 401,
        "freight_transport_unit_id": 101,
        "driver_id": 55,
        "driver_name": "Motorista Historico",
        "started_at": NOW,
        "ended_at": LATER,
        "actual_driver_amount": Decimal("2300.00"),
    }
    row.update(changes)
    return row


def make_expense_row(**changes):
    row = {
        "freight_expense_id": 501,
        "expense_type": "DESCARGA",
        "custom_description": None,
        "value": Decimal("300.00"),
        "occurred_at": LATER,
        "observation": "Descarga no destino",
        "is_considered": True,
    }
    row.update(changes)
    return row


def make_event_row(**changes):
    row = {
        "freight_event_id": 601,
        "event_type": "COMPLETED",
        "previous_status": "IN_PROGRESS",
        "new_status": "COMPLETED",
        "observation": "Entrega concluida",
        "occurred_at": LATER,
        "user_id": 7,
    }
    row.update(changes)
    return row


def make_financial_row(**changes):
    row = {
        "freight_financial_result_id": 8,
        "contracted_revenue": Decimal("11200.00"),
        "actual_driver_amount": Decimal("4300.00"),
        "toll_amount": Decimal("100.00"),
        "actual_expenses_total": Decimal("300.00"),
        "freight_insurance_total": Decimal("10.00"),
        "tax_total": Decimal("1120.00"),
        "administrative_cost_allocated": Decimal("480.00"),
        "total_cost": Decimal("6310.00"),
        "realized_result": Decimal("4890.00"),
        "realized_margin": Decimal("0.7749603803"),
        "finalized_at": LATER + timedelta(hours=1),
    }
    row.update(changes)
    return row


def detail_batches(
    *,
    base=None,
    units=None,
    assignments=None,
    expenses=None,
    events=None,
    financial=None,
):
    return (
        (base or make_base_row(),),
        tuple(units if units is not None else (make_unit_row(),)),
        tuple(
            assignments
            if assignments is not None
            else (make_assignment_row(),)
        ),
        tuple(expenses if expenses is not None else (make_expense_row(),)),
        tuple(events if events is not None else (make_event_row(),)),
        tuple(financial if financial is not None else (make_financial_row(),)),
    )


def compile_sql(statement) -> str:
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


class FreightQueryRepositoryTests(unittest.TestCase):

    def test_list_maps_projection_without_loading_aggregate(self):
        session = FakeSession(batches=((make_base_row(),),))
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
        session = FakeSession(batches=((
            make_base_row(
                customer_legal_name="Razao Antiga SA",
                customer_trade_name=None,
                customer_name="Razao Antiga SA",
            ),
        ),))
        repository = SqlAlchemyFreightQueryRepository(session)

        item = repository.list(FreightQueryFilters())[0]

        self.assertEqual(item.customer_name, "Razao Antiga SA")
        sql = compile_sql(session.statements[0])
        self.assertIn("customer_trade_name_snapshot", sql)
        self.assertIn("customer_legal_name_snapshot", sql)
        self.assertNotIn("JOIN customers", sql)

    def test_list_applies_customer_status_and_completion_filters(self):
        session = FakeSession(batches=((),))
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
        session = FakeSession(batches=((),))
        repository = SqlAlchemyFreightQueryRepository(session)

        repository.list(FreightQueryFilters())

        sql = compile_sql(session.statements[0])
        self.assertIn("sum(approved_version.contracted_price)", sql)
        self.assertIn("approved_quote.freight_id = freights.freight_id", sql)
        self.assertIn("approved_quote.current_status = 'APPROVED'", sql)

    def test_details_maps_operational_financial_and_history_read_model(self):
        second_unit = make_unit_row(
            freight_transport_unit_id=102,
            position=2,
            freight_vehicle_record_id=None,
            vehicle_type=None,
            plate=None,
            axle_count=None,
            pallet_capacity_min=None,
            pallet_capacity_max=None,
            payload_capacity_kg=None,
        )
        active_assignment = make_assignment_row(
            freight_driver_assignment_id=402,
            freight_transport_unit_id=102,
            driver_id=56,
            driver_name="Motorista Atual",
            started_at=LATER,
            ended_at=None,
            actual_driver_amount=None,
        )
        ignored_expense = make_expense_row(
            freight_expense_id=502,
            expense_type="OUTROS",
            custom_description="Estacionamento",
            value=Decimal("99.00"),
            is_considered=False,
        )
        created_event = make_event_row(
            freight_event_id=600,
            event_type="CREATED",
            previous_status=None,
            new_status="PENDING",
            occurred_at=NOW - timedelta(hours=1),
        )

        session = FakeSession(
            batches=detail_batches(
                units=(make_unit_row(), second_unit),
                assignments=(
                    make_assignment_row(),
                    active_assignment,
                ),
                expenses=(
                    make_expense_row(),
                    ignored_expense,
                ),
                events=(created_event, make_event_row()),
            )
        )
        repository = SqlAlchemyFreightQueryRepository(session)

        result = repository.get_by_id(77)

        self.assertIsNotNone(result)
        self.assertEqual(result.freight_id, 77)
        self.assertEqual(result.approved_complementary_quote_count, 2)
        self.assertEqual(len(result.transport_units), 2)

        unit_1 = result.transport_units[0]
        self.assertEqual(unit_1.position, 1)
        self.assertIsNotNone(unit_1.vehicle)
        self.assertEqual(
            unit_1.vehicle.vehicle_type,
            FreightVehicleType.CARRETA_LS,
        )
        self.assertEqual(unit_1.vehicle.plate, "ABC1D23")
        self.assertEqual(len(unit_1.driver_assignments), 1)
        self.assertFalse(unit_1.driver_assignments[0].is_active)
        self.assertEqual(
            unit_1.driver_assignments[0].actual_driver_amount,
            Decimal("2300.00"),
        )

        unit_2 = result.transport_units[1]
        self.assertIsNone(unit_2.vehicle)
        self.assertTrue(unit_2.driver_assignments[0].is_active)

        self.assertEqual(len(result.expenses), 2)
        self.assertEqual(
            result.expenses[0].expense_type,
            FreightExpenseType.DESCARGA,
        )
        self.assertFalse(result.expenses[1].is_considered)
        self.assertEqual(
            result.expenses[1].custom_description,
            "Estacionamento",
        )

        self.assertEqual(len(result.events), 2)
        self.assertEqual(
            result.events[0].event_type,
            FreightEventType.CREATED,
        )
        self.assertEqual(
            result.events[1].new_status,
            FreightStatus.COMPLETED,
        )

        self.assertTrue(result.financially_closed)
        self.assertIsNotNone(result.financial_result)
        self.assertEqual(
            result.financial_result.total_cost,
            Decimal("6310.00"),
        )
        self.assertEqual(
            result.financial_result.realized_result,
            Decimal("4890.00"),
        )

    def test_details_without_financial_close_returns_none_snapshot(self):
        session = FakeSession(
            batches=detail_batches(
                base=make_base_row(
                    financial_result_id=None,
                ),
                financial=(),
            )
        )
        repository = SqlAlchemyFreightQueryRepository(session)

        result = repository.get_by_id(77)

        self.assertIsNotNone(result)
        self.assertFalse(result.financially_closed)
        self.assertIsNone(result.financial_result_id)
        self.assertIsNone(result.financial_result)

    def test_details_uses_targeted_projection_queries(self):
        session = FakeSession(batches=detail_batches())
        repository = SqlAlchemyFreightQueryRepository(session)

        repository.get_by_id(77)

        self.assertEqual(len(session.statements), 6)
        sql = "\n".join(
            compile_sql(statement)
            for statement in session.statements
        )
        self.assertIn("freight_transport_units", sql)
        self.assertIn("freight_vehicle_records", sql)
        self.assertIn("freight_driver_assignments", sql)
        self.assertIn("JOIN drivers", sql)
        self.assertIn("freight_expenses", sql)
        self.assertIn("freight_events", sql)
        self.assertIn("freight_financial_results", sql)
        self.assertNotIn("driver_contacts", sql)
        self.assertNotIn("driver_addresses", sql)
        self.assertNotIn("driver_bank_accounts", sql)

    def test_details_returns_none_when_freight_does_not_exist(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession(batches=((),))
        )

        self.assertIsNone(repository.get_by_id(999))

    def test_missing_historical_route_is_reported_as_persistence_error(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession(batches=((make_base_row(origin=None),),))
        )

        with self.assertRaisesRegex(
            FreightPersistenceError,
            "origem ausente",
        ):
            repository.list(FreightQueryFilters())

    def test_sqlalchemy_error_in_list_is_wrapped(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession(batches=(SQLAlchemyError("boom"),))
        )

        with self.assertRaisesRegex(
            FreightPersistenceError,
            "lista de fretes",
        ):
            repository.list(FreightQueryFilters())

    def test_sqlalchemy_error_in_detail_is_wrapped(self):
        repository = SqlAlchemyFreightQueryRepository(
            FakeSession(
                batches=(
                    (make_base_row(),),
                    SQLAlchemyError("boom"),
                )
            )
        )

        with self.assertRaisesRegex(
            FreightPersistenceError,
            "detalhes do frete",
        ):
            repository.get_by_id(77)

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
