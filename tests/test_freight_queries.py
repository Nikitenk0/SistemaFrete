import unittest
from datetime import datetime, timezone
from decimal import Decimal

from application.dtos.freight_query import (
    FreightDetails,
    FreightListItem,
    FreightQueryFilters,
)
from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
)
from application.use_cases.get_freight_details import (
    GetFreightDetails,
)
from application.use_cases.list_freights import ListFreights
from domain.models.freight import FreightStatus


NOW = datetime(
    2026,
    8,
    25,
    18,
    0,
    tzinfo=timezone.utc,
)


class FakeFreightQueryRepository:

    def __init__(self):
        self.received_filters = None
        self.received_freight_id = None
        self.list_result = ()
        self.detail_result = None

    def list(self, filters):
        self.received_filters = filters
        return self.list_result

    def get_by_id(self, freight_id):
        self.received_freight_id = freight_id
        return self.detail_result


def make_list_item() -> FreightListItem:
    return FreightListItem(
        freight_id=10,
        customer_id=20,
        customer_name="Cliente ABC",
        primary_quote_id=30,
        primary_quote_number="ORC-2026-00001",
        origin="Curitiba/PR",
        destination="São Paulo/SP",
        current_status=FreightStatus.COMPLETED,
        contracted_revenue=Decimal("11200.00"),
        financially_closed=True,
        created_at=NOW,
        started_at=NOW,
        completed_at=NOW,
    )


def make_details() -> FreightDetails:
    return FreightDetails(
        freight_id=10,
        customer_id=20,
        customer_legal_name="Cliente ABC Ltda",
        customer_trade_name="Cliente ABC",
        primary_quote_id=30,
        primary_quote_number="ORC-2026-00001",
        origin="Curitiba/PR",
        destination="São Paulo/SP",
        current_status=FreightStatus.COMPLETED,
        contracted_revenue=Decimal("11200.00"),
        approved_complementary_quote_count=1,
        financially_closed=True,
        financial_result_id=40,
        created_at=NOW,
        started_at=NOW,
        completed_at=NOW,
    )


class ListFreightsTests(unittest.TestCase):

    def test_lists_without_filters(self):
        repository = FakeFreightQueryRepository()
        repository.list_result = (make_list_item(),)

        result = ListFreights(repository).execute()

        self.assertEqual(result, repository.list_result)
        self.assertEqual(
            repository.received_filters,
            FreightQueryFilters(),
        )

    def test_forwards_customer_status_and_completion_period(self):
        repository = FakeFreightQueryRepository()
        start = datetime(2026, 8, 1, tzinfo=timezone.utc)
        end = datetime(2026, 8, 31, 23, 59, tzinfo=timezone.utc)

        ListFreights(repository).execute(
            customer_id=20,
            status=FreightStatus.COMPLETED,
            completed_from=start,
            completed_to=end,
        )

        self.assertEqual(
            repository.received_filters,
            FreightQueryFilters(
                customer_id=20,
                status=FreightStatus.COMPLETED,
                completed_from=start,
                completed_to=end,
            ),
        )

    def test_accepts_completion_period_without_explicit_status(self):
        repository = FakeFreightQueryRepository()

        ListFreights(repository).execute(
            completed_from=NOW,
        )

        self.assertEqual(
            repository.received_filters.completed_from,
            NOW,
        )
        self.assertIsNone(
            repository.received_filters.status
        )

    def test_rejects_invalid_customer_id(self):
        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "customer_id inválido",
        ):
            ListFreights(
                FakeFreightQueryRepository()
            ).execute(
                customer_id=0,
            )

    def test_rejects_inverted_completion_period(self):
        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "Período de conclusão inválido",
        ):
            ListFreights(
                FakeFreightQueryRepository()
            ).execute(
                completed_from=NOW,
                completed_to=datetime(
                    2026,
                    8,
                    1,
                    tzinfo=timezone.utc,
                ),
            )

    def test_rejects_completion_period_with_non_completed_status(self):
        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "status COMPLETED",
        ):
            ListFreights(
                FakeFreightQueryRepository()
            ).execute(
                status=FreightStatus.IN_PROGRESS,
                completed_from=NOW,
            )


class GetFreightDetailsTests(unittest.TestCase):

    def test_returns_details(self):
        repository = FakeFreightQueryRepository()
        repository.detail_result = make_details()

        result = GetFreightDetails(
            repository
        ).execute(10)

        self.assertEqual(result, repository.detail_result)
        self.assertEqual(repository.received_freight_id, 10)

    def test_rejects_invalid_freight_id(self):
        with self.assertRaisesRegex(
            InvalidFreightDataError,
            "freight_id inválido",
        ):
            GetFreightDetails(
                FakeFreightQueryRepository()
            ).execute(0)

    def test_raises_not_found(self):
        with self.assertRaisesRegex(
            FreightNotFoundError,
            "Frete não encontrado",
        ):
            GetFreightDetails(
                FakeFreightQueryRepository()
            ).execute(999)


if __name__ == "__main__":
    unittest.main()
