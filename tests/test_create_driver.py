import unittest
from dataclasses import replace
from datetime import date

from application.exceptions import (
    DriverAlreadyExistsError,
    InvalidDriverDataError
)
from application.use_cases.create_driver import (
    CreateDriver
)
from domain.models.driver import (
    Driver
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

    def __init__(self):
        self.items: dict[int, Driver] = {}
        self.next_id = 1
        self.last_cpf_query: str | None = None

    def add(
        self,
        driver: Driver
    ) -> Driver:
        created = replace(
            driver,
            driver_id=self.next_id
        )
        self.items[
            self.next_id
        ] = created
        self.next_id += 1
        return created

    def get_by_id(
        self,
        driver_id: int
    ) -> Driver | None:
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


def complete_payload() -> dict:
    return {
        "name": "João da Silva",
        "cpf": "123.456.789-01",
        "rg": "12.345.678-9",
        "birth_date": date(1985, 5, 20),
        "cnh_number": "12345678900",
        "cnh_category": "D",
        "cnh_expiration_date": date(2030, 5, 20),
        "contacts": (
            DriverContact(
                phone="11999998888",
                is_primary=True
            ),
        ),
        "addresses": (
            DriverAddress(
                postal_code="01234567",
                street="Rua Exemplo",
                number="100",
                district="Centro",
                city="São Paulo",
                state="SP",
                is_primary=True
            ),
        ),
        "bank_accounts": (
            DriverBankAccount(
                bank_code="001",
                agency="1234",
                account="98765",
                account_type=(
                    DriverBankAccountType.CHECKING
                ),
                is_primary=True
            ),
        ),
        "created_by": 7,
    }


class CreateDriverTests(unittest.TestCase):

    def setUp(self):
        self.repository = FakeDriverRepository()
        self.unit_of_work = FakeDriverUnitOfWork(
            self.repository
        )
        self.use_case = CreateDriver(
            FakeDriverUnitOfWorkFactory(
                self.unit_of_work
            )
        )

    def test_creates_complete_driver_and_commits(self):
        created = self.use_case.execute(
            **complete_payload()
        )

        self.assertEqual(
            created.driver_id,
            1
        )
        self.assertEqual(
            created.cpf,
            "12345678901"
        )
        self.assertEqual(
            len(created.contacts),
            1
        )
        self.assertEqual(
            len(created.addresses),
            1
        )
        self.assertEqual(
            len(created.bank_accounts),
            1
        )
        self.assertTrue(
            self.unit_of_work.committed
        )

    def test_duplicate_cpf_is_rejected(self):
        self.use_case.execute(
            **complete_payload()
        )

        with self.assertRaises(
            DriverAlreadyExistsError
        ):
            self.use_case.execute(
                **complete_payload()
            )

    def test_cpf_is_normalized_before_duplicate_lookup(self):
        self.use_case.execute(
            **complete_payload()
        )

        self.assertEqual(
            self.repository.last_cpf_query,
            "12345678901"
        )

    def test_invalid_driver_data_is_wrapped(self):
        payload = complete_payload()
        payload["cpf"] = "123"

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )

    def test_invalid_created_by_is_wrapped(self):
        payload = complete_payload()
        payload["created_by"] = 0

        with self.assertRaises(
            InvalidDriverDataError
        ):
            self.use_case.execute(
                **payload
            )


if __name__ == "__main__":
    unittest.main()
