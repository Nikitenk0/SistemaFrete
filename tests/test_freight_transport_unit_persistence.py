import unittest
from datetime import (
    datetime,
    timezone
)

from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from infrastructure.persistence.sqlalchemy.base import (
    Base
)
import infrastructure.persistence.sqlalchemy.models  # noqa: F401
from infrastructure.persistence.sqlalchemy.freight_transport_unit_repository import (
    SqlAlchemyFreightTransportUnitRepository
)
from infrastructure.persistence.sqlalchemy.freight_unit_of_work import (
    SqlAlchemyFreightUnitOfWork
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightTransportUnitModel
)


NOW = datetime(
    2026,
    8,
    24,
    20,
    45,
    tzinfo=timezone.utc
)


class FreightTransportUnitPersistenceMetadataTests(
    unittest.TestCase
):

    def test_registers_transport_units_table(
        self
    ) -> None:

        table = Base.metadata.tables[
            "freight_transport_units"
        ]

        for column_name in (
            "freight_transport_unit_id",
            "freight_id",
            "position",
            "created_at",
            "created_by"
        ):
            self.assertIn(
                column_name,
                table.c
            )

        self.assertFalse(
            table.c.freight_id.nullable
        )
        self.assertFalse(
            table.c.position.nullable
        )

    def test_registers_expected_constraints(
        self
    ) -> None:

        table = Base.metadata.tables[
            "freight_transport_units"
        ]

        freight_fk = next(
            iter(
                table.c.freight_id.foreign_keys
            )
        )
        created_by_fk = next(
            iter(
                table.c.created_by.foreign_keys
            )
        )

        self.assertEqual(
            freight_fk.target_fullname,
            "freights.freight_id"
        )
        self.assertEqual(
            freight_fk.ondelete,
            "CASCADE"
        )
        self.assertEqual(
            created_by_fk.target_fullname,
            "users.user_id"
        )
        self.assertEqual(
            created_by_fk.ondelete,
            "SET NULL"
        )

        unique_constraints = {
            constraint.name
            for constraint in table.constraints
            if constraint.__class__.__name__
            == "UniqueConstraint"
        }

        self.assertIn(
            (
                "uq_freight_transport_units_"
                "freight_id_position"
            ),
            unique_constraints
        )

        check_constraints = {
            constraint.name
            for constraint in table.constraints
            if constraint.__class__.__name__
            == "CheckConstraint"
        }

        self.assertIn(
            (
                "ck_freight_transport_units_"
                "position_positive"
            ),
            check_constraints
        )


class FreightTransportUnitRepositoryMappingTests(
    unittest.TestCase
):

    def test_maps_domain_unit_to_model(
        self
    ) -> None:

        unit = FreightTransportUnit(
            freight_id=12,
            position=2,
            created_at=NOW,
            created_by=7
        )

        model = (
            SqlAlchemyFreightTransportUnitRepository
            ._to_model(
                unit
            )
        )

        self.assertEqual(
            model.freight_id,
            12
        )
        self.assertEqual(
            model.position,
            2
        )
        self.assertEqual(
            model.created_at,
            NOW
        )
        self.assertEqual(
            model.created_by,
            7
        )

    def test_maps_persisted_unit_to_domain(
        self
    ) -> None:

        model = FreightTransportUnitModel(
            freight_transport_unit_id=31,
            freight_id=12,
            position=2,
            created_at=NOW,
            created_by=7
        )

        unit = (
            SqlAlchemyFreightTransportUnitRepository
            ._to_domain(
                model
            )
        )

        self.assertEqual(
            unit.freight_transport_unit_id,
            31
        )
        self.assertEqual(
            unit.freight_id,
            12
        )
        self.assertEqual(
            unit.position,
            2
        )
        self.assertEqual(
            unit.created_at,
            NOW
        )
        self.assertEqual(
            unit.created_by,
            7
        )

    def test_count_returns_repository_scalar(
        self
    ) -> None:

        class FakeSession:
            def scalar(
                self,
                _statement
            ):
                return 3

        repository = (
            SqlAlchemyFreightTransportUnitRepository(
                FakeSession()
            )
        )

        self.assertEqual(
            repository.count_by_freight_id(
                12
            ),
            3
        )


class FreightUnitOfWorkIntegrationTests(
    unittest.TestCase
):

    def test_exposes_transport_unit_repository(
        self
    ) -> None:

        class FakeSession:
            def close(self):
                pass

            def rollback(self):
                pass

        fake_session = FakeSession()

        unit_of_work = SqlAlchemyFreightUnitOfWork(
            lambda: fake_session
        )

        with unit_of_work as active:
            self.assertIsInstance(
                active.transport_units,
                SqlAlchemyFreightTransportUnitRepository
            )


if __name__ == "__main__":
    unittest.main()
