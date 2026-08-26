import unittest
from datetime import datetime, timezone

from application.use_cases.get_transport_provider_details import (
    GetTransportProviderDetails,
)
from domain.models.driver import Driver, DriverStatus
from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
    DriverTransportProviderRole,
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
    2026,
    8,
    26,
    13,
    0,
    tzinfo=timezone.utc,
)


def make_driver(driver_id=10):
    return Driver(
        driver_id=driver_id,
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


def make_vehicle(vehicle_id=20):
    return Vehicle(
        vehicle_id=vehicle_id,
        plate="ABC1D23",
        vehicle_type=VehicleType.TRUCK,
    )


class ProviderRepo:
    def get_by_id(self, provider_id):
        if provider_id != 30:
            return None
        return TransportProvider(
            transport_provider_id=30,
            legal_name="Exemplo 123 Transportes LTDA",
            trade_name="Exemplo 123",
            tax_document="12345678000190",
            provider_type=TransportProviderType.COMPANY,
        )


class DriverAffRepo:
    def list_active_by_provider_id(self, provider_id):
        if provider_id != 30:
            return ()
        return (
            DriverTransportProviderAffiliation(
                driver_transport_provider_affiliation_id=1,
                driver_id=10,
                transport_provider_id=30,
                role=DriverTransportProviderRole.OWNER,
                started_at=NOW,
            ),
        )


class VehicleAffRepo:
    def list_active_by_provider_id(self, provider_id):
        if provider_id != 30:
            return ()
        return (
            VehicleTransportProviderAffiliation(
                vehicle_transport_provider_affiliation_id=2,
                vehicle_id=20,
                transport_provider_id=30,
                relation=VehicleTransportProviderRelation.OWNED,
                started_at=NOW,
            ),
        )


class DriverRepo:
    def get_by_id(self, driver_id):
        if driver_id == 10:
            return make_driver()
        return None


class VehicleRepo:
    def get_by_id(self, vehicle_id):
        if vehicle_id == 20:
            return make_vehicle()
        return None


class Uow:
    providers = ProviderRepo()
    driver_affiliations = DriverAffRepo()
    vehicle_affiliations = VehicleAffRepo()
    drivers = DriverRepo()
    vehicles = VehicleRepo()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self):
        pass

    def rollback(self):
        pass


class Factory:
    def create(self):
        return Uow()


class GetTransportProviderDetailsTests(
    unittest.TestCase
):

    def test_returns_provider_with_active_driver_and_vehicle(self):
        result = GetTransportProviderDetails(
            Factory()
        ).execute(30)

        self.assertEqual(
            result.provider.trade_name,
            "Exemplo 123",
        )
        self.assertEqual(
            len(result.drivers),
            1,
        )
        self.assertEqual(
            result.drivers[0].driver_id,
            10,
        )
        self.assertEqual(
            result.drivers[0].role,
            DriverTransportProviderRole.OWNER,
        )
        self.assertEqual(
            len(result.vehicles),
            1,
        )
        self.assertEqual(
            result.vehicles[0].vehicle_id,
            20,
        )
        self.assertEqual(
            result.vehicles[0].relation,
            VehicleTransportProviderRelation.OWNED,
        )


if __name__ == "__main__":
    unittest.main()
