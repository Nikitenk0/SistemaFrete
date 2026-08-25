import unittest
from datetime import (
    datetime,
    timedelta,
    timezone
)
from decimal import Decimal

from application.exceptions import (
    FreightDriverAssignmentNotFoundError
)
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from infrastructure.persistence.sqlalchemy.base import Base
import infrastructure.persistence.sqlalchemy.models  # noqa: F401
from infrastructure.persistence.sqlalchemy.freight_driver_assignment_repository import (
    SqlAlchemyFreightDriverAssignmentRepository
)
from infrastructure.persistence.sqlalchemy.freight_transport_unit_repository import (
    SqlAlchemyFreightTransportUnitRepository
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightDriverAssignmentModel,
    FreightTransportUnitModel
)


STARTED_AT = datetime(
    2026,
    8,
    25,
    8,
    0,
    tzinfo=timezone.utc
)
ENDED_AT = STARTED_AT + timedelta(
    hours=5
)
CREATED_AT = STARTED_AT - timedelta(
    minutes=10
)
UPDATED_AT = ENDED_AT


class FreightDriverAssignmentPersistenceMetadataTests(
    unittest.TestCase
):

    def test_registers_expected_table_and_columns(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_driver_assignments"
        ]

        for column_name in (
            "freight_driver_assignment_id",
            "freight_transport_unit_id",
            "driver_id",
            "started_at",
            "ended_at",
            "actual_driver_amount",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by"
        ):
            self.assertIn(
                column_name,
                table.c
            )

        self.assertFalse(
            table.c.freight_transport_unit_id.nullable
        )
        self.assertFalse(
            table.c.driver_id.nullable
        )
        self.assertFalse(
            table.c.started_at.nullable
        )
        self.assertTrue(
            table.c.ended_at.nullable
        )
        self.assertTrue(
            table.c.actual_driver_amount.nullable
        )

    def test_registers_expected_foreign_keys(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_driver_assignments"
        ]

        unit_fk = next(
            iter(
                table.c.freight_transport_unit_id.foreign_keys
            )
        )
        driver_fk = next(
            iter(
                table.c.driver_id.foreign_keys
            )
        )

        self.assertEqual(
            unit_fk.target_fullname,
            (
                "freight_transport_units."
                "freight_transport_unit_id"
            )
        )
        self.assertEqual(
            unit_fk.ondelete,
            "CASCADE"
        )
        self.assertEqual(
            driver_fk.target_fullname,
            "drivers.driver_id"
        )
        self.assertEqual(
            driver_fk.ondelete,
            "RESTRICT"
        )

    def test_registers_active_assignment_unique_indexes(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_driver_assignments"
        ]

        indexes = {
            index.name: index
            for index in table.indexes
        }

        self.assertTrue(
            indexes[
                "uq_freight_driver_assignments_active_unit"
            ].unique
        )
        self.assertTrue(
            indexes[
                "uq_freight_driver_assignments_active_driver"
            ].unique
        )

    def test_registers_lifecycle_check_constraints(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_driver_assignments"
        ]

        constraints = {
            constraint.name
            for constraint in table.constraints
            if constraint.__class__.__name__
            == "CheckConstraint"
        }

        self.assertIn(
            (
                "ck_freight_driver_assignments_"
                "actual_driver_amount_non_negative"
            ),
            constraints
        )
        self.assertIn(
            (
                "ck_freight_driver_assignments_"
                "completion_pair"
            ),
            constraints
        )
        self.assertIn(
            (
                "ck_freight_driver_assignments_"
                "ended_after_started"
            ),
            constraints
        )


class FreightDriverAssignmentRepositoryMappingTests(
    unittest.TestCase
):

    def test_maps_active_domain_assignment_to_model(
        self
    ) -> None:
        assignment = FreightDriverAssignment(
            freight_transport_unit_id=21,
            driver_id=8,
            started_at=STARTED_AT,
            created_at=CREATED_AT,
            created_by=4,
            updated_at=CREATED_AT,
            updated_by=4
        )

        model = (
            SqlAlchemyFreightDriverAssignmentRepository
            ._to_model(
                assignment
            )
        )

        self.assertEqual(
            model.freight_transport_unit_id,
            21
        )
        self.assertEqual(
            model.driver_id,
            8
        )
        self.assertEqual(
            model.started_at,
            STARTED_AT
        )
        self.assertIsNone(
            model.ended_at
        )
        self.assertIsNone(
            model.actual_driver_amount
        )

    def test_maps_finished_model_to_domain(
        self
    ) -> None:
        model = FreightDriverAssignmentModel(
            freight_driver_assignment_id=31,
            freight_transport_unit_id=21,
            driver_id=8,
            started_at=STARTED_AT,
            ended_at=ENDED_AT,
            actual_driver_amount=Decimal("2450.50"),
            created_at=CREATED_AT,
            created_by=4,
            updated_at=UPDATED_AT,
            updated_by=5
        )

        assignment = (
            SqlAlchemyFreightDriverAssignmentRepository
            ._to_domain(
                model
            )
        )

        self.assertEqual(
            assignment.freight_driver_assignment_id,
            31
        )
        self.assertFalse(
            assignment.is_active
        )
        self.assertEqual(
            assignment.actual_driver_amount,
            Decimal("2450.50")
        )
        self.assertEqual(
            assignment.updated_by,
            5
        )

    def test_save_updates_only_operational_completion_fields(
        self
    ) -> None:
        model = FreightDriverAssignmentModel(
            freight_driver_assignment_id=31,
            freight_transport_unit_id=21,
            driver_id=8,
            started_at=STARTED_AT,
            ended_at=None,
            actual_driver_amount=None,
            created_at=CREATED_AT,
            created_by=4,
            updated_at=CREATED_AT,
            updated_by=4
        )

        class FakeSession:
            def scalar(
                self,
                _statement
            ):
                return model

            def flush(self):
                pass

        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                FakeSession()
            )
        )

        saved = repository.save(
            FreightDriverAssignment(
                freight_driver_assignment_id=31,
                freight_transport_unit_id=21,
                driver_id=8,
                started_at=STARTED_AT,
                ended_at=ENDED_AT,
                actual_driver_amount=Decimal("2450.50"),
                created_at=CREATED_AT,
                created_by=4,
                updated_at=UPDATED_AT,
                updated_by=5
            )
        )

        self.assertEqual(
            saved.ended_at,
            ENDED_AT
        )
        self.assertEqual(
            saved.actual_driver_amount,
            Decimal("2450.50")
        )
        self.assertEqual(
            model.driver_id,
            8
        )
        self.assertEqual(
            model.started_at,
            STARTED_AT
        )

    def test_save_rejects_missing_persisted_assignment(
        self
    ) -> None:

        class FakeSession:
            def scalar(
                self,
                _statement
            ):
                return None

        repository = (
            SqlAlchemyFreightDriverAssignmentRepository(
                FakeSession()
            )
        )

        with self.assertRaises(
            FreightDriverAssignmentNotFoundError
        ):
            repository.save(
                FreightDriverAssignment(
                    freight_driver_assignment_id=31,
                    freight_transport_unit_id=21,
                    driver_id=8,
                    started_at=STARTED_AT,
                    ended_at=ENDED_AT,
                    actual_driver_amount=Decimal("1.00"),
                    created_at=CREATED_AT,
                    created_by=4,
                    updated_at=UPDATED_AT,
                    updated_by=5
                )
            )


class FreightTransportUnitRepositoryE7Tests(
    unittest.TestCase
):

    def test_get_by_id_maps_transport_unit(
        self
    ) -> None:
        model = FreightTransportUnitModel(
            freight_transport_unit_id=21,
            freight_id=7,
            position=2,
            created_at=CREATED_AT,
            created_by=4
        )

        class FakeSession:
            def scalar(
                self,
                _statement
            ):
                return model

        repository = (
            SqlAlchemyFreightTransportUnitRepository(
                FakeSession()
            )
        )

        result = repository.get_by_id(
            21
        )

        self.assertIsInstance(
            result,
            FreightTransportUnit
        )
        self.assertEqual(
            result.freight_id,
            7
        )
        self.assertEqual(
            result.position,
            2
        )


if __name__ == "__main__":
    unittest.main()
