import unittest
from datetime import date

from application.dtos.driver_query import (
    DriverListItem
)
from application.exceptions import (
    DriverNotFoundError,
    InvalidDriverDataError
)
from application.use_cases.get_driver import (
    GetDriver
)
from application.use_cases.list_drivers import (
    ListDrivers
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


class FakeDriverQueryRepository:

    def __init__(self):
        self.calls = []
        self.result = (
            DriverListItem(
                driver_id=10,
                name="Motorista Teste",
                cpf="12345678909",
                cnh_number="99887766",
                cnh_category="E",
                cnh_expiration_date=date(
                    2030,
                    5,
                    10
                ),
                status=DriverStatus.ACTIVE,
                primary_phone="41999990000",
                primary_email=None
            ),
        )

    def list(
        self,
        query="",
        status=None,
        limit=100
    ):
        self.calls.append(
            (query, status, limit)
        )
        return self.result


class FakeDriverRepository:

    def __init__(
        self,
        driver: Driver | None
    ):
        self.driver = driver

    def get_by_id(
        self,
        driver_id: int
    ) -> Driver | None:
        if (
            self.driver is not None
            and self.driver.driver_id == driver_id
        ):
            return self.driver
        return None


class FakeDriverUnitOfWork:

    def __init__(
        self,
        driver: Driver | None
    ):
        self.drivers = FakeDriverRepository(
            driver
        )

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def commit(self):
        pass

    def rollback(self):
        pass


class FakeDriverUnitOfWorkFactory:

    def __init__(
        self,
        driver: Driver | None
    ):
        self.driver = driver

    def create(self):
        return FakeDriverUnitOfWork(
            self.driver
        )


def make_driver() -> Driver:
    return Driver(
        driver_id=10,
        name="Motorista Teste",
        cpf="12345678909",
        rg="1234567",
        birth_date=date(1985, 5, 10),
        cnh_number="99887766",
        cnh_category="E",
        cnh_expiration_date=date(2030, 5, 10),
        status=DriverStatus.ACTIVE,
        contacts=(
            DriverContact(
                phone="41999990000",
                is_primary=True
            ),
        ),
        addresses=(
            DriverAddress(
                postal_code="80000000",
                street="Rua Teste",
                number="123",
                district="Centro",
                city="Curitiba",
                state="PR",
                is_primary=True
            ),
        ),
        bank_accounts=(
            DriverBankAccount(
                bank_code="001",
                agency="1234",
                account="98765",
                account_type=(
                    DriverBankAccountType.CHECKING
                ),
                is_primary=True
            ),
        )
    )


class ListDriversTests(unittest.TestCase):

    def test_lists_without_query(self):
        repository = FakeDriverQueryRepository()
        result = ListDrivers(
            repository
        ).execute()

        self.assertEqual(
            len(result),
            1
        )
        self.assertEqual(
            repository.calls[-1],
            ("", None, 100)
        )

    def test_normalizes_query_and_status(self):
        repository = FakeDriverQueryRepository()
        ListDrivers(
            repository
        ).execute(
            query="  João  ",
            status="ACTIVE",
            limit=25
        )

        self.assertEqual(
            repository.calls[-1],
            (
                "João",
                DriverStatus.ACTIVE,
                25
            )
        )

    def test_rejects_invalid_status(self):
        with self.assertRaises(
            InvalidDriverDataError
        ):
            ListDrivers(
                FakeDriverQueryRepository()
            ).execute(
                status="BLOCKED"
            )

    def test_rejects_invalid_limit(self):
        use_case = ListDrivers(
            FakeDriverQueryRepository()
        )

        for limit in (0, 201):
            with self.assertRaises(
                InvalidDriverDataError
            ):
                use_case.execute(
                    limit=limit
                )


class GetDriverTests(unittest.TestCase):

    def test_returns_complete_driver(self):
        driver = make_driver()
        result = GetDriver(
            FakeDriverUnitOfWorkFactory(
                driver
            )
        ).execute(
            10
        )

        self.assertEqual(
            result,
            driver
        )
        self.assertEqual(
            len(result.contacts),
            1
        )
        self.assertEqual(
            len(result.addresses),
            1
        )
        self.assertEqual(
            len(result.bank_accounts),
            1
        )

    def test_rejects_invalid_id(self):
        with self.assertRaises(
            InvalidDriverDataError
        ):
            GetDriver(
                FakeDriverUnitOfWorkFactory(
                    None
                )
            ).execute(
                0
            )

    def test_rejects_missing_driver(self):
        with self.assertRaises(
            DriverNotFoundError
        ):
            GetDriver(
                FakeDriverUnitOfWorkFactory(
                    None
                )
            ).execute(
                10
            )


if __name__ == "__main__":
    unittest.main()
