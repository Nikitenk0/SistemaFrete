import unittest
from datetime import date

from domain.models.driver import (
    Driver,
    DriverStatus
)
from domain.models.driver_address import (
    DriverAddress
)
from domain.models.driver_bank_account import (
    DriverBankAccount,
    DriverBankAccountType,
    DriverPixKeyType
)
from domain.models.driver_contact import (
    DriverContact
)


def make_contact(
    *,
    primary: bool = True
) -> DriverContact:
    return DriverContact(
        phone="(11) 99999-8888",
        secondary_phone="11 3333-4444",
        email=" MOTORISTA@EXAMPLE.COM ",
        is_primary=primary
    )


def make_address(
    *,
    primary: bool = True
) -> DriverAddress:
    return DriverAddress(
        postal_code="01234-567",
        street=" Rua Exemplo ",
        number=" 100 ",
        complement=" Apto 12 ",
        district=" Centro ",
        city=" São Paulo ",
        state="sp",
        is_primary=primary
    )


def make_bank_account(
    *,
    primary: bool = True
) -> DriverBankAccount:
    return DriverBankAccount(
        bank_code="001",
        agency="1234",
        account="98765",
        account_digit="4",
        account_type=(
            DriverBankAccountType.CHECKING
        ),
        pix_key_type=DriverPixKeyType.CPF,
        pix_key="12345678901",
        is_primary=primary
    )


def make_driver(
    **overrides
) -> Driver:
    data = {
        "name": " João da Silva ",
        "cpf": "123.456.789-01",
        "rg": " 12.345.678-9 ",
        "birth_date": date(1985, 5, 20),
        "cnh_number": " 12345678900 ",
        "cnh_category": " d ",
        "cnh_expiration_date": date(2030, 5, 20),
        "contacts": (make_contact(),),
        "addresses": (make_address(),),
        "bank_accounts": (make_bank_account(),),
    }
    data.update(
        overrides
    )
    return Driver(
        **data
    )


class DriverTests(unittest.TestCase):

    def test_complete_driver_is_valid(self):
        driver = make_driver()

        self.assertEqual(
            driver.name,
            "João da Silva"
        )
        self.assertEqual(
            driver.cpf,
            "12345678901"
        )
        self.assertEqual(
            driver.rg,
            "12.345.678-9"
        )
        self.assertEqual(
            driver.cnh_number,
            "12345678900"
        )
        self.assertEqual(
            driver.cnh_category,
            "D"
        )
        self.assertEqual(
            driver.status,
            DriverStatus.ACTIVE
        )

    def test_contact_normalizes_phone_and_email(self):
        contact = make_contact()

        self.assertEqual(
            contact.phone,
            "11999998888"
        )
        self.assertEqual(
            contact.secondary_phone,
            "1133334444"
        )
        self.assertEqual(
            contact.email,
            "motorista@example.com"
        )

    def test_address_normalizes_postal_code_and_state(self):
        address = make_address()

        self.assertEqual(
            address.postal_code,
            "01234567"
        )
        self.assertEqual(
            address.state,
            "SP"
        )
        self.assertEqual(
            address.street,
            "Rua Exemplo"
        )

    def test_bank_account_requires_valid_bank_code(self):
        with self.assertRaises(ValueError):
            DriverBankAccount(
                bank_code="1",
                agency="1234",
                account="999",
                account_type=(
                    DriverBankAccountType.CHECKING
                ),
                is_primary=True
            )

    def test_bank_account_requires_pix_key_with_type(self):
        with self.assertRaises(ValueError):
            DriverBankAccount(
                bank_code="001",
                agency="1234",
                account="999",
                account_type=(
                    DriverBankAccountType.CHECKING
                ),
                pix_key_type=DriverPixKeyType.EMAIL,
                pix_key=None,
                is_primary=True
            )

    def test_invalid_cpf_is_rejected(self):
        with self.assertRaises(ValueError):
            make_driver(
                cpf="123"
            )

    def test_future_birth_date_is_rejected(self):
        with self.assertRaises(ValueError):
            make_driver(
                birth_date=date(2999, 1, 1)
            )

    def test_cnh_expiration_must_be_after_birth_date(self):
        with self.assertRaises(ValueError):
            make_driver(
                cnh_expiration_date=date(1980, 1, 1)
            )

    def test_driver_requires_contact(self):
        with self.assertRaises(ValueError):
            make_driver(
                contacts=()
            )

    def test_driver_requires_address(self):
        with self.assertRaises(ValueError):
            make_driver(
                addresses=()
            )

    def test_driver_requires_bank_account(self):
        with self.assertRaises(ValueError):
            make_driver(
                bank_accounts=()
            )

    def test_driver_requires_exactly_one_primary_contact(self):
        with self.assertRaises(ValueError):
            make_driver(
                contacts=(
                    make_contact(primary=True),
                    make_contact(primary=True)
                )
            )

    def test_driver_requires_exactly_one_primary_address(self):
        with self.assertRaises(ValueError):
            make_driver(
                addresses=(
                    make_address(primary=False),
                )
            )

    def test_driver_requires_exactly_one_primary_bank_account(self):
        with self.assertRaises(ValueError):
            make_driver(
                bank_accounts=(
                    make_bank_account(primary=False),
                )
            )


if __name__ == "__main__":
    unittest.main()
