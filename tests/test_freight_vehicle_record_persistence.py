import unittest
from datetime import (
    datetime,
    timezone
)

from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType
)
from infrastructure.persistence.sqlalchemy.base import Base
import infrastructure.persistence.sqlalchemy.models  # noqa: F401
from infrastructure.persistence.sqlalchemy.freight_vehicle_record_repository import (
    SqlAlchemyFreightVehicleRecordRepository
)
from infrastructure.persistence.sqlalchemy.freight_vehicle_record_unit_of_work import (
    SqlAlchemyFreightVehicleRecordUnitOfWork
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightVehicleRecordModel
)


CREATED_AT = datetime(
    2026,
    8,
    25,
    12,
    0,
    tzinfo=timezone.utc
)


def make_record() -> FreightVehicleRecord:
    return FreightVehicleRecord(
        freight_transport_unit_id=21,
        vehicle_type=FreightVehicleType.CARRETA_LS,
        plate="ABC1D23",
        axle_count=6,
        pallet_capacity_min=28,
        pallet_capacity_max=28,
        payload_capacity_kg=30000,
        created_at=CREATED_AT,
        created_by=4
    )


class FreightVehicleRecordPersistenceMetadataTests(
    unittest.TestCase
):

    def test_registers_expected_table_and_columns(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_vehicle_records"
        ]

        for column_name in (
            "freight_vehicle_record_id",
            "freight_transport_unit_id",
            "vehicle_type",
            "plate",
            "axle_count",
            "pallet_capacity_min",
            "pallet_capacity_max",
            "payload_capacity_kg",
            "created_at",
            "created_by"
        ):
            self.assertIn(
                column_name,
                table.c
            )

        self.assertFalse(
            table.c.freight_transport_unit_id.nullable
        )
        self.assertFalse(
            table.c.vehicle_type.nullable
        )
        self.assertFalse(
            table.c.plate.nullable
        )

    def test_registers_expected_foreign_keys(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_vehicle_records"
        ]

        unit_fk = next(
            iter(
                table.c.freight_transport_unit_id.foreign_keys
            )
        )
        created_by_fk = next(
            iter(
                table.c.created_by.foreign_keys
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
            created_by_fk.target_fullname,
            "users.user_id"
        )
        self.assertEqual(
            created_by_fk.ondelete,
            "SET NULL"
        )

    def test_registers_one_vehicle_per_transport_unit_constraint(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_vehicle_records"
        ]

        unique_constraints = {
            constraint.name
            for constraint in table.constraints
            if constraint.__class__.__name__
            == "UniqueConstraint"
        }

        self.assertIn(
            (
                "uq_freight_vehicle_records_"
                "freight_transport_unit_id"
            ),
            unique_constraints
        )

    def test_registers_vehicle_integrity_checks(
        self
    ) -> None:
        table = Base.metadata.tables[
            "freight_vehicle_records"
        ]

        constraints = {
            constraint.name
            for constraint in table.constraints
            if constraint.__class__.__name__
            == "CheckConstraint"
        }

        self.assertIn(
            "ck_freight_vehicle_records_vehicle_type",
            constraints
        )
        self.assertIn(
            "ck_freight_vehicle_records_plate",
            constraints
        )
        self.assertIn(
            "ck_freight_vehicle_records_specification",
            constraints
        )


class FreightVehicleRecordRepositoryMappingTests(
    unittest.TestCase
):

    def test_maps_domain_record_to_model(
        self
    ) -> None:
        model = (
            SqlAlchemyFreightVehicleRecordRepository
            ._to_model(
                make_record()
            )
        )

        self.assertEqual(
            model.freight_transport_unit_id,
            21
        )
        self.assertEqual(
            model.vehicle_type,
            "CARRETA_LS"
        )
        self.assertEqual(
            model.plate,
            "ABC1D23"
        )
        self.assertEqual(
            model.axle_count,
            6
        )
        self.assertEqual(
            model.pallet_capacity_min,
            28
        )
        self.assertEqual(
            model.pallet_capacity_max,
            28
        )
        self.assertEqual(
            model.payload_capacity_kg,
            30000
        )
        self.assertEqual(
            model.created_at,
            CREATED_AT
        )

    def test_maps_persisted_model_to_domain(
        self
    ) -> None:
        model = FreightVehicleRecordModel(
            freight_vehicle_record_id=31,
            freight_transport_unit_id=21,
            vehicle_type="TRUCK",
            plate="DEF4G56",
            axle_count=3,
            pallet_capacity_min=16,
            pallet_capacity_max=20,
            payload_capacity_kg=12500,
            created_at=CREATED_AT,
            created_by=4
        )

        record = (
            SqlAlchemyFreightVehicleRecordRepository
            ._to_domain(
                model
            )
        )

        self.assertEqual(
            record.freight_vehicle_record_id,
            31
        )
        self.assertEqual(
            record.vehicle_type,
            FreightVehicleType.TRUCK
        )
        self.assertEqual(
            record.pallet_capacity_min,
            16
        )
        self.assertEqual(
            record.pallet_capacity_max,
            20
        )
        self.assertEqual(
            record.payload_capacity_kg,
            12500
        )

    def test_get_by_transport_unit_id_maps_record(
        self
    ) -> None:
        model = FreightVehicleRecordModel(
            freight_vehicle_record_id=31,
            freight_transport_unit_id=21,
            vehicle_type="TOCO",
            plate="GHI7J89",
            axle_count=2,
            pallet_capacity_min=12,
            pallet_capacity_max=12,
            payload_capacity_kg=6500,
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
            SqlAlchemyFreightVehicleRecordRepository(
                FakeSession()
            )
        )

        result = repository.get_by_transport_unit_id(
            21
        )

        self.assertIsNotNone(
            result
        )
        self.assertEqual(
            result.vehicle_type,
            FreightVehicleType.TOCO
        )


class FreightVehicleRecordUnitOfWorkTests(
    unittest.TestCase
):

    def test_exposes_vehicle_record_repository(
        self
    ) -> None:

        class FakeSession:
            def close(self):
                pass

            def rollback(self):
                pass

        fake_session = FakeSession()

        unit_of_work = (
            SqlAlchemyFreightVehicleRecordUnitOfWork(
                lambda: fake_session
            )
        )

        with unit_of_work as active:
            self.assertIsInstance(
                active.vehicle_records,
                SqlAlchemyFreightVehicleRecordRepository
            )


if __name__ == "__main__":
    unittest.main()
