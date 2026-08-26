import unittest
from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    InvalidTransportProviderDataError,
    InvalidTransportProviderStateError,
)
from application.use_cases.create_transport_provider import (
    CreateTransportProvider,
)
from application.use_cases.set_driver_transport_provider_affiliation import (
    SetDriverTransportProviderAffiliation,
)
from application.use_cases.set_vehicle_transport_provider_affiliation import (
    SetVehicleTransportProviderAffiliation,
)
from application.use_cases.validate_transport_combination import (
    ValidateTransportCombination,
)
from domain.models.driver import Driver, DriverStatus
from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
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
    2026, 8, 26, 12, 0,
    tzinfo=timezone.utc,
)


def make_driver(driver_id=10, cpf="12345678901"):
    return Driver(
        driver_id=driver_id,
        name="João",
        cpf=cpf,
        rg="RG1",
        birth_date=datetime(1980, 1, 1).date(),
        cnh_number="CNH1",
        cnh_category="D",
        cnh_expiration_date=datetime(2030, 1, 1).date(),
        status=DriverStatus.ACTIVE,
        contacts=(type("C", (), {"is_primary": True})(),),
        addresses=(type("A", (), {"is_primary": True})(),),
        bank_accounts=(type("B", (), {"is_primary": True})(),),
    )


def make_vehicle(vehicle_id=20):
    return Vehicle(
        vehicle_id=vehicle_id,
        plate="ABC1D23",
        vehicle_type=VehicleType.TRUCK,
        status=VehicleStatus.ACTIVE,
    )


def make_provider(provider_id=30):
    return TransportProvider(
        transport_provider_id=provider_id,
        legal_name="Exemplo 123 Transportes LTDA",
        trade_name="Exemplo 123",
        tax_document="12345678000190",
        provider_type=TransportProviderType.COMPANY,
        status=TransportProviderStatus.ACTIVE,
    )


class EntityRepo:
    def __init__(self, value=None):
        self.value = value

    def get_by_id(self, _id):
        return self.value

    def get_by_id_for_update(self, _id):
        return self.value


class ProviderRepo(EntityRepo):
    def __init__(self, value=None):
        super().__init__(value)
        self.added = None

    def get_by_tax_document(self, document):
        if (
            self.value is not None
            and self.value.tax_document == document
        ):
            return self.value
        return None

    def add(self, provider):
        self.added = replace(
            provider,
            transport_provider_id=30,
        )
        self.value = self.added
        return self.added

    def save(self, provider):
        self.value = provider
        return provider

    def search(self, **_kwargs):
        return (
            (self.value,)
            if self.value is not None
            else ()
        )


class DriverAffRepo:
    def __init__(self, current=None):
        self.current = current
        self.history = (
            [current]
            if current is not None
            else []
        )

    def get_active_by_driver_id(self, _id):
        return (
            self.current
            if (
                self.current is not None
                and self.current.is_active
            )
            else None
        )

    def add(self, affiliation):
        created = replace(
            affiliation,
            driver_transport_provider_affiliation_id=101,
        )
        self.current = created
        self.history.append(created)
        return created

    def save(self, affiliation):
        self.current = (
            affiliation
            if affiliation.is_active
            else None
        )
        self.history.append(affiliation)
        return affiliation


class VehicleAffRepo:
    def __init__(self, current=None):
        self.current = current
        self.history = (
            [current]
            if current is not None
            else []
        )

    def get_active_by_vehicle_id(self, _id):
        return (
            self.current
            if (
                self.current is not None
                and self.current.is_active
            )
            else None
        )

    def add(self, affiliation):
        created = replace(
            affiliation,
            vehicle_transport_provider_affiliation_id=201,
        )
        self.current = created
        self.history.append(created)
        return created

    def save(self, affiliation):
        self.current = (
            affiliation
            if affiliation.is_active
            else None
        )
        self.history.append(affiliation)
        return affiliation


class FakeUow:
    def __init__(
        self,
        provider=None,
        driver=None,
        vehicle=None,
        driver_affiliation=None,
        vehicle_affiliation=None,
    ):
        self.providers = ProviderRepo(provider)
        self.drivers = EntityRepo(driver)
        self.vehicles = EntityRepo(vehicle)
        self.driver_affiliations = DriverAffRepo(
            driver_affiliation
        )
        self.vehicle_affiliations = VehicleAffRepo(
            vehicle_affiliation
        )
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class Factory:
    def __init__(self, uow):
        self.uow = uow

    def create(self):
        return self.uow


class TransportProviderUseCaseTests(unittest.TestCase):

    def test_creates_company_provider(self):
        uow = FakeUow()

        result = CreateTransportProvider(
            Factory(uow)
        ).execute(
            legal_name="Exemplo 123 Transportes LTDA",
            trade_name="Exemplo 123",
            tax_document="12.345.678/0001-90",
            provider_type=TransportProviderType.COMPANY,
        )

        self.assertEqual(
            result.transport_provider_id,
            30,
        )
        self.assertTrue(uow.committed)

    def test_links_owner_driver_to_company(self):
        uow = FakeUow(
            provider=make_provider(),
            driver=make_driver(),
        )

        result = SetDriverTransportProviderAffiliation(
            Factory(uow)
        ).execute(
            driver_id=10,
            transport_provider_id=30,
            role=DriverTransportProviderRole.OWNER,
            changed_at=NOW,
        )

        self.assertEqual(
            result.transport_provider_id,
            30,
        )
        self.assertEqual(
            result.role,
            DriverTransportProviderRole.OWNER,
        )
        self.assertTrue(uow.committed)

    def test_links_owned_vehicle_to_company(self):
        uow = FakeUow(
            provider=make_provider(),
            vehicle=make_vehicle(),
        )

        result = SetVehicleTransportProviderAffiliation(
            Factory(uow)
        ).execute(
            vehicle_id=20,
            transport_provider_id=30,
            relation=VehicleTransportProviderRelation.OWNED,
            changed_at=NOW,
        )

        self.assertEqual(
            result.transport_provider_id,
            30,
        )
        self.assertTrue(uow.committed)

    def test_replaces_previous_driver_provider_preserving_history(self):
        old = DriverTransportProviderAffiliation(
            driver_transport_provider_affiliation_id=1,
            driver_id=10,
            transport_provider_id=99,
            role=DriverTransportProviderRole.EMPLOYEE,
            started_at=NOW,
        )
        uow = FakeUow(
            provider=make_provider(),
            driver=make_driver(),
            driver_affiliation=old,
        )

        result = SetDriverTransportProviderAffiliation(
            Factory(uow)
        ).execute(
            driver_id=10,
            transport_provider_id=30,
            role=DriverTransportProviderRole.OWNER,
            changed_at=NOW,
        )

        self.assertEqual(
            result.transport_provider_id,
            30,
        )
        self.assertTrue(
            any(
                item.ended_at == NOW
                for item in uow.driver_affiliations.history
            )
        )

    def test_individual_owner_must_match_driver_cpf(self):
        provider = TransportProvider(
            transport_provider_id=31,
            legal_name="Autônomo",
            tax_document="99999999999",
            provider_type=TransportProviderType.INDIVIDUAL,
        )
        uow = FakeUow(
            provider=provider,
            driver=make_driver(
                cpf="12345678901"
            ),
        )

        with self.assertRaisesRegex(
            InvalidTransportProviderDataError,
            "mesmo CPF",
        ):
            SetDriverTransportProviderAffiliation(
                Factory(uow)
            ).execute(
                driver_id=10,
                transport_provider_id=31,
                role=DriverTransportProviderRole.OWNER,
                changed_at=NOW,
            )

    def test_validates_same_provider_driver_vehicle_combination(self):
        driver_aff = DriverTransportProviderAffiliation(
            driver_transport_provider_affiliation_id=1,
            driver_id=10,
            transport_provider_id=30,
            role=DriverTransportProviderRole.OWNER,
            started_at=NOW,
        )
        vehicle_aff = VehicleTransportProviderAffiliation(
            vehicle_transport_provider_affiliation_id=2,
            vehicle_id=20,
            transport_provider_id=30,
            relation=VehicleTransportProviderRelation.OWNED,
            started_at=NOW,
        )
        uow = FakeUow(
            provider=make_provider(),
            driver=make_driver(),
            vehicle=make_vehicle(),
            driver_affiliation=driver_aff,
            vehicle_affiliation=vehicle_aff,
        )

        result = ValidateTransportCombination(
            Factory(uow)
        ).execute(
            transport_provider_id=30,
            driver_id=10,
            vehicle_id=20,
        )

        self.assertEqual(
            result.transport_provider_id,
            30,
        )

    def test_rejects_vehicle_from_other_provider(self):
        driver_aff = DriverTransportProviderAffiliation(
            driver_transport_provider_affiliation_id=1,
            driver_id=10,
            transport_provider_id=30,
            role=DriverTransportProviderRole.OWNER,
            started_at=NOW,
        )
        vehicle_aff = VehicleTransportProviderAffiliation(
            vehicle_transport_provider_affiliation_id=2,
            vehicle_id=20,
            transport_provider_id=99,
            relation=VehicleTransportProviderRelation.OWNED,
            started_at=NOW,
        )
        uow = FakeUow(
            provider=make_provider(),
            driver=make_driver(),
            vehicle=make_vehicle(),
            driver_affiliation=driver_aff,
            vehicle_affiliation=vehicle_aff,
        )

        with self.assertRaisesRegex(
            InvalidTransportProviderStateError,
            "Veículo não possui vínculo ativo",
        ):
            ValidateTransportCombination(
                Factory(uow)
            ).execute(
                transport_provider_id=30,
                driver_id=10,
                vehicle_id=20,
            )


if __name__ == "__main__":
    unittest.main()
