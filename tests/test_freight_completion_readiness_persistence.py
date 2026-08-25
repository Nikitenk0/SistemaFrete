import unittest
from datetime import (
    datetime,
    timedelta,
    timezone
)
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from application.exceptions import (
    FreightDriverAssignmentPersistenceError
)
from infrastructure.persistence.sqlalchemy.freight_driver_assignment_repository import (
    SqlAlchemyFreightDriverAssignmentRepository
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightDriverAssignmentModel
)


NOW = datetime(
    2026,
    8,
    25,
    14,
    0,
    tzinfo=timezone.utc
)


class FakeScalarResult:

    def __init__(
        self,
        models
    ):
        self._models = models

    def all(self):
        return self._models


class CapturingSession:

    def __init__(
        self,
        models=()
    ):
        self.models = models
        self.statement = None

    def scalars(
        self,
        statement
    ):
        self.statement = statement
        return FakeScalarResult(
            self.models
        )


class FailingSession:

    def scalars(
        self,
        statement
    ):
        raise SQLAlchemyError(
            "falha simulada"
        )


class DriverAssignmentHistoryByFreightTests(
    unittest.TestCase
):

    def test_query_filters_all_assignments_by_freight(
        self
    ) -> None:
        session = CapturingSession()
        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                session
            )
        )

        result = repository.list_by_freight_id(
            77
        )

        self.assertEqual(
            result,
            ()
        )

        statement_text = str(
            session.statement
        )

        self.assertIn(
            "JOIN freight_transport_units",
            statement_text
        )
        self.assertIn(
            "freight_transport_units.freight_id",
            statement_text
        )
        self.assertNotIn(
            "freight_driver_assignments.ended_at IS NULL",
            statement_text
        )
        self.assertIn(
            "freight_transport_units.position",
            statement_text
        )
        self.assertIn(
            "freight_driver_assignments.started_at",
            statement_text
        )

    def test_maps_active_and_closed_assignments_for_freight(
        self
    ) -> None:
        models = (
            FreightDriverAssignmentModel(
                freight_driver_assignment_id=101,
                freight_transport_unit_id=11,
                driver_id=21,
                started_at=NOW,
                ended_at=(
                    NOW + timedelta(hours=2)
                ),
                actual_driver_amount=Decimal(
                    "2000.00"
                ),
                created_at=NOW,
                created_by=3,
                updated_at=(
                    NOW + timedelta(hours=2)
                ),
                updated_by=3
            ),
            FreightDriverAssignmentModel(
                freight_driver_assignment_id=102,
                freight_transport_unit_id=12,
                driver_id=22,
                started_at=NOW,
                ended_at=None,
                actual_driver_amount=None,
                created_at=NOW,
                created_by=3,
                updated_at=NOW,
                updated_by=3
            )
        )

        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                CapturingSession(
                    models
                )
            )
        )

        result = repository.list_by_freight_id(
            77
        )

        self.assertEqual(
            len(result),
            2
        )
        self.assertFalse(
            result[0].is_active
        )
        self.assertEqual(
            result[0].actual_driver_amount,
            Decimal("2000.00")
        )
        self.assertTrue(
            result[1].is_active
        )

    def test_wraps_sqlalchemy_error(
        self
    ) -> None:
        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                FailingSession()
            )
        )

        with self.assertRaisesRegex(
            FreightDriverAssignmentPersistenceError,
            "participações de motorista do frete"
        ):
            repository.list_by_freight_id(
                77
            )


if __name__ == "__main__":
    unittest.main()
