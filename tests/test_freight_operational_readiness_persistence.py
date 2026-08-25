import unittest
from datetime import (
    datetime,
    timezone
)

from infrastructure.persistence.sqlalchemy.freight_driver_assignment_repository import (
    SqlAlchemyFreightDriverAssignmentRepository
)
from infrastructure.persistence.sqlalchemy.freight_unit_of_work import (
    SqlAlchemyFreightUnitOfWork
)
from infrastructure.persistence.sqlalchemy.freight_vehicle_record_repository import (
    SqlAlchemyFreightVehicleRecordRepository
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightDriverAssignmentModel
)


NOW = datetime(
    2026,
    8,
    25,
    13,
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


class ActiveDriverAssignmentsByFreightTests(
    unittest.TestCase
):

    def test_query_filters_active_assignments_by_freight(
        self
    ) -> None:
        session = CapturingSession()
        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                session
            )
        )

        result = repository.list_active_by_freight_id(
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
        self.assertIn(
            "freight_driver_assignments.ended_at IS NULL",
            statement_text
        )

    def test_maps_active_assignments_returned_for_freight(
        self
    ) -> None:
        models = (
            FreightDriverAssignmentModel(
                freight_driver_assignment_id=101,
                freight_transport_unit_id=11,
                driver_id=21,
                started_at=NOW,
                ended_at=None,
                actual_driver_amount=None,
                created_at=NOW,
                created_by=3,
                updated_at=NOW,
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

        session = CapturingSession(
            models
        )
        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                session
            )
        )

        result = repository.list_active_by_freight_id(
            77
        )

        self.assertEqual(
            len(result),
            2
        )
        self.assertEqual(
            result[0].freight_transport_unit_id,
            11
        )
        self.assertEqual(
            result[1].driver_id,
            22
        )
        self.assertTrue(
            all(
                assignment.is_active
                for assignment in result
            )
        )


class FakeUnitOfWorkSession:

    def __init__(self):
        self.closed = False
        self.committed = False
        self.rolled_back = False

    def close(self) -> None:
        self.closed = True

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class FreightUnitOfWorkReadinessWiringTests(
    unittest.TestCase
):

    def test_exposes_readiness_repositories_using_same_session(
        self
    ) -> None:
        session = FakeUnitOfWorkSession()
        unit_of_work = SqlAlchemyFreightUnitOfWork(
            lambda: session
        )

        with unit_of_work as active_unit_of_work:
            self.assertIsInstance(
                active_unit_of_work.driver_assignments,
                SqlAlchemyFreightDriverAssignmentRepository
            )
            self.assertIsInstance(
                active_unit_of_work.vehicle_records,
                SqlAlchemyFreightVehicleRecordRepository
            )
            self.assertIs(
                active_unit_of_work.driver_assignments._session,
                session
            )
            self.assertIs(
                active_unit_of_work.vehicle_records._session,
                session
            )

        self.assertTrue(
            session.closed
        )

    def test_properties_are_unavailable_before_enter(
        self
    ) -> None:
        unit_of_work = SqlAlchemyFreightUnitOfWork(
            FakeUnitOfWorkSession
        )

        with self.assertRaises(
            RuntimeError
        ):
            _ = unit_of_work.driver_assignments

        with self.assertRaises(
            RuntimeError
        ):
            _ = unit_of_work.vehicle_records

    def test_properties_are_cleared_after_exit(
        self
    ) -> None:
        unit_of_work = SqlAlchemyFreightUnitOfWork(
            FakeUnitOfWorkSession
        )

        with unit_of_work:
            pass

        with self.assertRaises(
            RuntimeError
        ):
            _ = unit_of_work.driver_assignments

        with self.assertRaises(
            RuntimeError
        ):
            _ = unit_of_work.vehicle_records


if __name__ == "__main__":
    unittest.main()
