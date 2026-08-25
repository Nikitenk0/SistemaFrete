import unittest
from dataclasses import replace
from datetime import (
    date,
    datetime,
    timezone
)

from application.exceptions import (
    DriverAlreadyExistsError,
    DriverNotFoundError,
    InvalidDriverDataError
)
from application.use_cases.update_driver import (
    UpdateDriver
)
from domain.models.driver import (
    Driver,
    DriverStatus
)
from domain.models.driver_address import (
    DriverAddress
)
from domain.models.driver_bank_account import (
    DriverBankAccount,
    DriverBankAccountType
)
from domain.models.driver_contact import (
    DriverContact
)


class FakeDriverRepository:

    def __init__(
        self,
        drivers: tuple[Driver, ...]
    ):
        self.items = {
            driver.driver_id: driver
            for driver in drivers
            if driver.driver_id is not None
        }
        self.locked_driver_id: int | None = None
        self.saved: Driver | None = None
        self.last_cpf_query: str | None = None

    def add(
        self,
        driver: Driver
    ) -> Driver:
        raise NotImplementedError

    def save(
        self,
        driver: Driver
    ) -> Driver:
        self.saved = driver
        self.items[driver.driver_id] = driver
        return driver

    def get_by_id(
        self,
        driver_id: int
    ) -> Driver | None:
        return self.items.get(
            driver_id
        )

    def get_by_id_for_update(
        self,
        driver_id: int
    ) -> Driver | None:
        self.locked_driver_id = driver_id
        return self.items.get(
            driver_id
        )

    def get_by_cpf(
        self,
        cpf: str
    ) -> Driver | None:
        self.last_cpf_query = cpf
        return next(
            (
                driver
                for driver in self.items.values()
                if driver.cpf == cpf
            ),
            None
        )

    def search(
        self,
        query: str,
        limit: int = 20
    ) -> tuple[Driver, ...]:
        return tuple(
            list(self.items.values())[:limit]
        )


class FakeDriverUnitOfWork:

    def __init__(
        self,
        repository: FakeDriverRepository
    ):
        self.drivers = repository
        self.committed = False
        self.rolled_back = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def __enter__(self):
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        traceback
    ) -> None:
        if exception_type is not None:
            self.rollback()


class FakeDriverUnitOfWorkFactory:

    def __init__(
        self,
        unit_of_work: FakeDriverUnitOfWork
    ):
        self.unit_of_work = unit_of_work

    def create(self) -> FakeDriverUnitOfWork:
        return self.unit_of_work


def make_driver(
    driver_id: int = 10,
    cpf: str = "12345678901"
) -> Driver:

    created_at = datetime(
        2026,
        1,
        10,
        tzinfo=timezone.utc
    )

    return Driver(
        driver_id=driver_id,
        name="Motorista Original",
        cpf=cpf,
        rg="RG-ORIGINAL",
        birth_date=date(1985, 5, 20),
        cnh_number="11111111111",
        cnh_category="D",
        cnh_expiration_date=date(2030, 5, 20),
        status=DriverStatus.ACTIVE,
        contacts=(
            DriverContact(
                driver_contact_id=101,
                driver_id=driver_id,
                phone="11999998888",
                email="original@example.com",
                is_primary=True,
                created_at=created_at,
                created_by=7
            ),
        ),
        addresses=(
            DriverAddress(
                driver_address_id=201,
                driver_id=driver_id,
                postal_code="01234567",
                street="Rua Original",
                number="100",
                district="Centro",
                city="São Paulo",
                state="SP",
                is_primary=True,
                created_at=created_at,
                created_by=7
            ),
        ),
        bank_accounts=(
            DriverBankAccount(
                driver_bank_account_id=301,
                driver_id=driver_id,
                bank_code="001",
                agency="1234",
                account="98765",
                account_type=(
                    DriverBankAccountType.CHECKING
                ),
                is_primary=True,
                created_at=created_at,
                created_by=7
            ),
        ),
        created_at=created_at,
        created_by=7,
        updated_at=created_at,
        updated_by=7
    )


def update_payload(
    current: Driver
) -> dict:

    return {
        "driver_id": current.driver_id,
        "name": "Motorista Corrigido",
        "cpf": "987.654.321-00",
        "rg": "RG-CORRIGIDO",
        "birth_date": date(1986, 6, 21),
        "cnh_number": "22222222222",
        "cnh_category": "E",
        "cnh_expiration_date": date(2032, 6, 21),
        "contacts": (
            replace(
                current.contacts[0],
                phone="11988887777",
                email="corrigido@example.com"
            ),
        ),
        "addresses": (
            replace(
                current.addresses[0],
                postal_code="80000000",
                street="Rua Corrigida",
                number="200",
                district="Centro",
                city="Curitiba",
                state="PR"
            ),
        ),
        "bank_accounts": (
            replace(
                current.bank_accounts[0],
                bank_code="341",
                agency="4321",
                account="12345",
                account_type=(
                    DriverBankAccountType.SAVINGS
                )
            ),
        ),
        "status": DriverStatus.INACTIVE,
        "updated_by": 9,
    }


class UpdateDriverTests(
    unittest.TestCase
):

    def setUp(self) -> None:
        self.current = make_driver()
        self.repository = FakeDriverRepository(
            (
                self.current,
            )
        )
        self.unit_of_work = FakeDriverUnitOfWork(
            self.repository
        )
        self.use_case = UpdateDriver(
            FakeDriverUnitOfWorkFactory(
                self.unit_of_work
            )
        )

    def test_updates_complete_driver_and_commits(
        self
    ) -> None:

        result = self.use_case.execute(
            **update_payload(
                self.current
            )
        )

        self.assertEqual(
            self.repository.locked_driver_id,
            10
        )
        self.assertEqual(
            result.driver_id,
            10
        )
        self.assertEqual(
            result.name,
            "Motorista Corrigido"
        )
        self.assertEqual(
            result.cpf,
            "98765432100"
        )
        self.assertEqual(
            result.cnh_category,
            "E"
        )
        self.assertEqual(
            result.status,
            DriverStatus.INACTIVE
        )
        self.assertEqual(
            result.contacts[0].phone,
            "11988887777"
        )
        self.assertEqual(
            result.addresses[0].state,
            "PR"
        )
        self.assertEqual(
            result.bank_accounts[0].bank_code,
            "341"
        )
        self.assertEqual(
            result.created_at,
            self.current.created_at
        )
        self.assertEqual(
            result.created_by,
            7
        )
        self.assertEqual(
            result.updated_by,
            9
        )
        self.assertTrue(
            self.unit_of_work.committed
        )

    def test_preserves_existing_child_identifiers_and_creation_audit(
        self
    ) -> None:

        result = self.use_case.execute(
            **update_payload(
                self.current
            )
        )

        self.assertEqual(
            result.contacts[0].driver_contact_id,
            101
        )
        self.assertEqual(
            result.contacts[0].created_by,
            7
        )
        self.assertEqual(
            result.addresses[0].driver_address_id,
            201
        )
        self.assertEqual(
            result.bank_accounts[0].driver_bank_account_id,
            301
        )
        self.assertEqual(
            result.contacts[0].updated_by,
            9
        )

    def test_accepts_new_secondary_contact(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        payload["contacts"] = (
            *payload["contacts"],
            DriverContact(
                phone="11977776666",
                is_primary=False
            ),
        )

        result = self.use_case.execute(
            **payload
        )

        self.assertEqual(
            len(result.contacts),
            2
        )
        self.assertIsNone(
            result.contacts[1].driver_contact_id
        )
        self.assertEqual(
            result.contacts[1].driver_id,
            10
        )
        self.assertEqual(
            result.contacts[1].created_by,
            9
        )

    def test_checks_duplicate_using_normalized_cpf(
        self
    ) -> None:

        self.use_case.execute(
            **update_payload(
                self.current
            )
        )

        self.assertEqual(
            self.repository.last_cpf_query,
            "98765432100"
        )

    def test_rejects_cpf_owned_by_another_driver(
        self
    ) -> None:

        other = make_driver(
            driver_id=20,
            cpf="98765432100"
        )
        self.repository.items[20] = other

        with self.assertRaises(
            DriverAlreadyExistsError
        ):
            self.use_case.execute(
                **update_payload(
                    self.current
                )
            )

        self.assertFalse(
            self.unit_of_work.committed
        )

    def test_allows_current_driver_to_keep_same_cpf(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        payload["cpf"] = "123.456.789-01"

        result = self.use_case.execute(
            **payload
        )

        self.assertEqual(
            result.cpf,
            "12345678901"
        )
        self.assertTrue(
            self.unit_of_work.committed
        )

    def test_rejects_missing_driver(
        self
    ) -> None:

        self.repository.items.clear()

        with self.assertRaises(
            DriverNotFoundError
        ):
            self.use_case.execute(
                **update_payload(
                    self.current
                )
            )

    def test_rejects_invalid_driver_id(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        payload["driver_id"] = 0

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )

    def test_rejects_invalid_updated_by(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        payload["updated_by"] = 0

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )

    def test_rejects_child_from_another_driver(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        payload["contacts"] = (
            replace(
                self.current.contacts[0],
                driver_id=999
            ),
        )

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )

    def test_rejects_duplicate_existing_child_id(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        first = payload["contacts"][0]
        payload["contacts"] = (
            first,
            replace(
                first,
                phone="11966665555",
                is_primary=False
            ),
        )

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )

    def test_rejects_invalid_domain_state(
        self
    ) -> None:

        payload = update_payload(
            self.current
        )
        payload["contacts"] = ()

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )


if __name__ == "__main__":
    unittest.main()
