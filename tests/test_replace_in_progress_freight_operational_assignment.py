import unittest
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from application.exceptions import (
    InvalidFreightStateError,
    InvalidTransportProviderStateError,
)
from application.use_cases.replace_in_progress_freight_operational_assignment import (
    ReplaceInProgressFreightOperationalAssignment,
)
from domain.models.driver import Driver, DriverStatus
from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
    DriverTransportProviderRole,
)
from domain.models.freight import Freight, FreightStatus
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment,
)
from domain.models.freight_operational_assignment import (
    FreightOperationalAssignment,
)
from domain.models.freight_transport_unit import FreightTransportUnit
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderType,
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
)
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderAffiliation,
    VehicleTransportProviderRelation,
)


NOW = datetime(
    2026, 8, 26, 14, 0,
    tzinfo=timezone.utc,
)


def make_driver(driver_id, name, cpf):
    return Driver(
        driver_id=driver_id,
        name=name,
        cpf=cpf,
        rg=f"RG{driver_id}",
        birth_date=datetime(1980, 1, 1).date(),
        cnh_number=f"CNH{driver_id}",
        cnh_category="D",
        cnh_expiration_date=datetime(2030, 1, 1).date(),
        status=DriverStatus.ACTIVE,
        contacts=(
            type("C", (), {"is_primary": True})(),
        ),
        addresses=(
            type("A", (), {"is_primary": True})(),
        ),
        bank_accounts=(
            type("B", (), {"is_primary": True})(),
        ),
    )


class MultiRepo:
    def __init__(self, values):
        self.values = values

    def get_by_id(self, item_id):
        return self.values.get(item_id)

    def get_by_id_for_update(self, item_id):
        return self.values.get(item_id)


class DriverAssignmentRepo:
    def __init__(self, current):
        self.current = current
        self.saved = None
        self.created = None

    def get_active_by_transport_unit_id(self, _unit_id):
        return (
            self.current
            if self.current.is_active
            else self.created
        )

    def get_active_by_driver_id(self, driver_id):
        if (
            self.current.is_active
            and self.current.driver_id == driver_id
        ):
            return self.current
        if (
            self.created is not None
            and self.created.is_active
            and self.created.driver_id == driver_id
        ):
            return self.created
        return None

    def save(self, assignment):
        self.saved = assignment
        self.current = assignment
        return assignment

    def add(self, assignment):
        self.created = replace(
            assignment,
            freight_driver_assignment_id=22,
        )
        return self.created


class VehicleRecordRepo:
    def __init__(self, current):
        self.current = current
        self.created = None
        self.deleted = False

    def get_by_transport_unit_id(self, _unit_id):
        return self.current

    def get_active_by_master_vehicle(
        self,
        vehicle_id,
        plate,
        exclude_transport_unit_id=None,
    ):
        return None

    def delete_by_transport_unit_id(self, _unit_id):
        self.deleted = True
        self.current = None

    def add(self, record):
        self.created = replace(
            record,
            freight_vehicle_record_id=42,
        )
        self.current = self.created
        return self.created


class DriverAffRepo:
    def __init__(self, provider_by_driver):
        self.provider_by_driver = provider_by_driver

    def get_active_by_driver_id(self, driver_id):
        provider_id = self.provider_by_driver.get(driver_id)
        if provider_id is None:
            return None
        return DriverTransportProviderAffiliation(
            driver_transport_provider_affiliation_id=(
                100 + driver_id
            ),
            driver_id=driver_id,
            transport_provider_id=provider_id,
            role=DriverTransportProviderRole.EMPLOYEE,
            started_at=NOW,
        )


class VehicleAffRepo:
    def __init__(self, provider_by_vehicle):
        self.provider_by_vehicle = provider_by_vehicle

    def get_active_by_vehicle_id(self, vehicle_id):
        provider_id = self.provider_by_vehicle.get(vehicle_id)
        if provider_id is None:
            return None
        return VehicleTransportProviderAffiliation(
            vehicle_transport_provider_affiliation_id=(
                200 + vehicle_id
            ),
            vehicle_id=vehicle_id,
            transport_provider_id=provider_id,
            relation=VehicleTransportProviderRelation.OWNED,
            started_at=NOW,
        )


class OperationalRepo:
    def __init__(self, current_context):
        self.current_context = current_context
        self.created = None

    def get_by_driver_assignment_id(self, assignment_id):
        if (
            self.current_context is not None
            and self.current_context.freight_driver_assignment_id
            == assignment_id
        ):
            return self.current_context
        return None

    def add(self, context):
        self.created = replace(
            context,
            freight_operational_assignment_id=102,
        )
        return self.created


class FakeUow:
    def __init__(
        self,
        *,
        current_context=True,
        new_driver_provider=40,
        new_vehicle_provider=40,
        new_vehicle_id=52,
    ):
        self.freights = MultiRepo({
            7: Freight(
                freight_id=7,
                customer_id=3,
                primary_quote_id=2,
                current_status=FreightStatus.IN_PROGRESS,
                started_at=NOW,
            )
        })
        self.transport_units = MultiRepo({
            11: FreightTransportUnit(
                freight_transport_unit_id=11,
                freight_id=7,
                position=1,
            )
        })

        current_assignment = FreightDriverAssignment(
            freight_driver_assignment_id=21,
            freight_transport_unit_id=11,
            driver_id=31,
            started_at=NOW,
        )
        self.driver_assignments = DriverAssignmentRepo(
            current_assignment
        )

        current_vehicle = FreightVehicleRecord(
            freight_vehicle_record_id=41,
            freight_transport_unit_id=11,
            vehicle_id=51,
            vehicle_type=FreightVehicleType.TRUCK,
            plate="ABC1D23",
            axle_count=3,
            pallet_capacity_min=16,
            pallet_capacity_max=20,
            payload_capacity_kg=12500,
        )
        self.vehicle_records = VehicleRecordRepo(
            current_vehicle
        )

        self.providers = MultiRepo({
            30: TransportProvider(
                transport_provider_id=30,
                legal_name="Exemplo 123 Transportes LTDA",
                trade_name="Exemplo 123",
                tax_document="12345678000190",
                provider_type=TransportProviderType.COMPANY,
            ),
            40: TransportProvider(
                transport_provider_id=40,
                legal_name="Exemplo 456 Transportes LTDA",
                trade_name="Exemplo 456",
                tax_document="98765432000110",
                provider_type=TransportProviderType.COMPANY,
            ),
        })

        self.drivers = MultiRepo({
            31: make_driver(
                31,
                "Joao",
                "12345678901",
            ),
            32: make_driver(
                32,
                "Carlos",
                "98765432100",
            ),
        })

        self.vehicles = MultiRepo({
            51: Vehicle(
                vehicle_id=51,
                plate="ABC1D23",
                vehicle_type=VehicleType.TRUCK,
                status=VehicleStatus.ACTIVE,
            ),
            52: Vehicle(
                vehicle_id=52,
                plate="DEF2E34",
                vehicle_type=VehicleType.TRUCK,
                status=VehicleStatus.ACTIVE,
            ),
        })

        self.driver_affiliations = DriverAffRepo({
            31: 30,
            32: new_driver_provider,
        })
        self.vehicle_affiliations = VehicleAffRepo({
            51: 30,
            52: new_vehicle_provider,
        })

        context = (
            FreightOperationalAssignment(
                freight_operational_assignment_id=101,
                freight_driver_assignment_id=21,
                transport_provider_id=30,
                vehicle_id=51,
                provider_name_snapshot="Exemplo 123",
                provider_tax_document_snapshot="12345678000190",
                driver_name_snapshot="Joao",
                driver_cpf_snapshot="12345678901",
                vehicle_plate_snapshot="ABC1D23",
                vehicle_type_snapshot=VehicleType.TRUCK,
            )
            if current_context
            else None
        )
        self.operational_assignments = OperationalRepo(
            context
        )

        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class Context:
    def __init__(self, uow):
        self.uow = uow

    def __enter__(self):
        return self.uow

    def __exit__(self, *_args):
        return None


class Factory:
    def __init__(self, uow):
        self.uow = uow

    def create(self):
        return Context(self.uow)


class ReplaceInProgressFreightOperationalAssignmentTests(
    unittest.TestCase
):

    def test_switches_from_company_123_to_company_456(self):
        uow = FakeUow()

        result = (
            ReplaceInProgressFreightOperationalAssignment(
                Factory(uow)
            ).execute(
                freight_transport_unit_id=11,
                transport_provider_id=40,
                driver_id=32,
                vehicle_id=52,
                actual_transport_amount=Decimal("500.00"),
                switched_at=NOW,
            )
        )

        self.assertEqual(
            uow.driver_assignments.saved.actual_driver_amount,
            Decimal("500.00"),
        )
        self.assertEqual(
            uow.driver_assignments.saved.ended_at,
            NOW,
        )
        self.assertEqual(
            uow.driver_assignments.created.driver_id,
            32,
        )
        self.assertTrue(
            uow.vehicle_records.deleted
        )
        self.assertEqual(
            uow.vehicle_records.created.vehicle_id,
            52,
        )
        self.assertEqual(
            result.transport_provider_id,
            40,
        )
        self.assertEqual(
            result.driver_name_snapshot,
            "Carlos",
        )
        self.assertEqual(
            result.vehicle_plate_snapshot,
            "DEF2E34",
        )
        self.assertTrue(
            uow.committed
        )

    def test_rejects_new_driver_from_other_provider(self):
        uow = FakeUow(
            new_driver_provider=30,
            new_vehicle_provider=40,
        )

        with self.assertRaisesRegex(
            InvalidTransportProviderStateError,
            "Motorista nao possui vinculo ativo",
        ):
            ReplaceInProgressFreightOperationalAssignment(
                Factory(uow)
            ).execute(
                freight_transport_unit_id=11,
                transport_provider_id=40,
                driver_id=32,
                vehicle_id=52,
                actual_transport_amount=Decimal("500.00"),
                switched_at=NOW,
            )

    def test_requires_current_context_before_switch(self):
        uow = FakeUow(
            current_context=False
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "Reconheca o conjunto operacional atual",
        ):
            ReplaceInProgressFreightOperationalAssignment(
                Factory(uow)
            ).execute(
                freight_transport_unit_id=11,
                transport_provider_id=40,
                driver_id=32,
                vehicle_id=52,
                actual_transport_amount=Decimal("500.00"),
                switched_at=NOW,
            )

    def test_driver_change_requires_vehicle_change(self):
        uow = FakeUow(
            new_driver_provider=30,
            new_vehicle_provider=40,
        )

        with self.assertRaisesRegex(
            InvalidFreightStateError,
            "selecione tambem outro veiculo",
        ):
            ReplaceInProgressFreightOperationalAssignment(
                Factory(uow)
            ).execute(
                freight_transport_unit_id=11,
                transport_provider_id=30,
                driver_id=32,
                vehicle_id=51,
                actual_transport_amount=Decimal("500.00"),
                switched_at=NOW,
            )


if __name__ == "__main__":
    unittest.main()
