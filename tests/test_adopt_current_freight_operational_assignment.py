import unittest
from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    InvalidTransportProviderStateError,
)
from application.use_cases.adopt_current_freight_operational_assignment import (
    AdoptCurrentFreightOperationalAssignment,
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
from domain.models.freight_transport_unit import (
    FreightTransportUnit,
)
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
    VehicleType,
)
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderAffiliation,
    VehicleTransportProviderRelation,
)


NOW = datetime(
    2026, 8, 26, 13, 0,
    tzinfo=timezone.utc,
)


class SingleRepo:
    def __init__(self, value):
        self.value = value

    def get_by_id(self, _id):
        return self.value

    def get_by_id_for_update(self, _id):
        return self.value


class DriverAssignmentRepo:
    def __init__(self, assignment):
        self.assignment = assignment

    def get_active_by_transport_unit_id(self, _id):
        return self.assignment


class VehicleRecordRepo:
    def __init__(self, record):
        self.record = record

    def get_by_transport_unit_id(self, _id):
        return self.record


class DriverAffiliationRepo:
    def __init__(self, value):
        self.value = value

    def get_active_by_driver_id(self, _id):
        return self.value


class VehicleAffiliationRepo:
    def __init__(self, value):
        self.value = value

    def get_active_by_vehicle_id(self, _id):
        return self.value


class OperationalRepo:
    def __init__(self, existing=None):
        self.existing = existing
        self.added = None

    def get_by_driver_assignment_id(self, _id):
        return self.existing

    def add(self, item):
        self.added = replace(
            item,
            freight_operational_assignment_id=100,
        )
        self.existing = self.added
        return self.added


def make_uow(
    driver_provider_id=30,
    vehicle_provider_id=30,
    existing=None,
):
    class Uow:
        pass

    uow = Uow()

    uow.transport_units = SingleRepo(
        FreightTransportUnit(
            freight_transport_unit_id=11,
            freight_id=7,
            position=1,
        )
    )
    uow.freights = SingleRepo(
        Freight(
            freight_id=7,
            customer_id=3,
            primary_quote_id=2,
            current_status=FreightStatus.IN_PROGRESS,
            started_at=NOW,
        )
    )
    uow.driver_assignments = DriverAssignmentRepo(
        FreightDriverAssignment(
            freight_driver_assignment_id=21,
            freight_transport_unit_id=11,
            driver_id=31,
            started_at=NOW,
        )
    )
    uow.vehicle_records = VehicleRecordRepo(
        FreightVehicleRecord(
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
    )
    uow.driver_affiliations = DriverAffiliationRepo(
        DriverTransportProviderAffiliation(
            driver_transport_provider_affiliation_id=61,
            driver_id=31,
            transport_provider_id=driver_provider_id,
            role=DriverTransportProviderRole.OWNER,
            started_at=NOW,
        )
    )
    uow.vehicle_affiliations = VehicleAffiliationRepo(
        VehicleTransportProviderAffiliation(
            vehicle_transport_provider_affiliation_id=71,
            vehicle_id=51,
            transport_provider_id=vehicle_provider_id,
            relation=VehicleTransportProviderRelation.OWNED,
            started_at=NOW,
        )
    )
    uow.providers = SingleRepo(
        TransportProvider(
            transport_provider_id=30,
            legal_name="Exemplo 123 Transportes LTDA",
            trade_name="Exemplo 123",
            tax_document="12345678000190",
            provider_type=TransportProviderType.COMPANY,
        )
    )
    uow.drivers = SingleRepo(
        Driver(
            driver_id=31,
            name="João",
            cpf="12345678901",
            rg="RG1",
            birth_date=datetime(1980, 1, 1).date(),
            cnh_number="CNH1",
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
    )
    uow.vehicles = SingleRepo(
        Vehicle(
            vehicle_id=51,
            plate="ABC1D23",
            vehicle_type=VehicleType.TRUCK,
        )
    )
    uow.operational_assignments = OperationalRepo(
        existing=existing
    )
    uow.committed = False

    def commit():
        uow.committed = True

    uow.commit = commit
    uow.rollback = lambda: None

    class Context:
        def __enter__(self):
            return uow

        def __exit__(self, *_args):
            return None

    class Factory:
        def create(self):
            return Context()

    return uow, Factory()


class AdoptCurrentFreightOperationalAssignmentTests(
    unittest.TestCase
):

    def test_adopts_current_provider_driver_vehicle(self):
        uow, factory = make_uow()

        result = AdoptCurrentFreightOperationalAssignment(
            factory
        ).execute(11)

        self.assertEqual(
            result.transport_provider_id,
            30,
        )
        self.assertEqual(
            result.freight_driver_assignment_id,
            21,
        )
        self.assertEqual(
            result.vehicle_id,
            51,
        )
        self.assertEqual(
            result.provider_name_snapshot,
            "Exemplo 123",
        )
        self.assertTrue(uow.committed)

    def test_rejects_driver_vehicle_from_different_providers(self):
        _uow, factory = make_uow(
            driver_provider_id=30,
            vehicle_provider_id=99,
        )

        with self.assertRaisesRegex(
            InvalidTransportProviderStateError,
            "prestadores diferentes",
        ):
            AdoptCurrentFreightOperationalAssignment(
                factory
            ).execute(11)

    def test_rejects_missing_driver_affiliation(self):
        uow, factory = make_uow()
        uow.driver_affiliations = DriverAffiliationRepo(
            None
        )

        with self.assertRaisesRegex(
            InvalidTransportProviderStateError,
            "Motorista ativo não possui vínculo",
        ):
            AdoptCurrentFreightOperationalAssignment(
                factory
            ).execute(11)

    def test_is_idempotent_when_context_already_exists(self):
        existing = FreightOperationalAssignment(
            freight_operational_assignment_id=100,
            freight_driver_assignment_id=21,
            transport_provider_id=30,
            vehicle_id=51,
            provider_name_snapshot="Exemplo 123",
            provider_tax_document_snapshot="12345678000190",
            driver_name_snapshot="João",
            driver_cpf_snapshot="12345678901",
            vehicle_plate_snapshot="ABC1D23",
            vehicle_type_snapshot=VehicleType.TRUCK,
        )
        uow, factory = make_uow(
            existing=existing
        )

        result = AdoptCurrentFreightOperationalAssignment(
            factory
        ).execute(11)

        self.assertEqual(
            result,
            existing,
        )
        self.assertFalse(
            uow.committed
        )


if __name__ == "__main__":
    unittest.main()
