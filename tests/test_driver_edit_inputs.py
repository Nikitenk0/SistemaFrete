import unittest
from datetime import date, datetime, timezone

from domain.models.driver import Driver, DriverStatus
from domain.models.driver_address import DriverAddress
from domain.models.driver_bank_account import (
    DriverBankAccount,
    DriverBankAccountType,
    DriverPixKeyType,
)
from domain.models.driver_contact import DriverContact
from presentation.desktop.driver_edit_inputs import (
    build_driver_update_form_data,
)
from presentation.desktop.driver_registration_inputs import (
    parse_driver_registration,
)


NOW = datetime(2026, 8, 25, tzinfo=timezone.utc)


def make_driver() -> Driver:
    return Driver(
        driver_id=10,
        name="Original",
        cpf="12345678901",
        rg="RG1",
        birth_date=date(1980, 1, 1),
        cnh_number="CNH1",
        cnh_category="D",
        cnh_expiration_date=date(2030, 1, 1),
        status=DriverStatus.ACTIVE,
        contacts=(
            DriverContact(
                driver_contact_id=101,
                driver_id=10,
                phone="41999998888",
                secondary_phone="4133334444",
                email="old@example.com",
                is_primary=True,
                created_at=NOW,
                created_by=7,
            ),
            DriverContact(
                driver_contact_id=102,
                driver_id=10,
                phone="41911112222",
                is_primary=False,
            ),
        ),
        addresses=(
            DriverAddress(
                driver_address_id=201,
                driver_id=10,
                postal_code="80000000",
                street="Rua A",
                number="1",
                district="Centro",
                city="Curitiba",
                state="PR",
                is_primary=True,
                created_at=NOW,
                created_by=7,
            ),
        ),
        bank_accounts=(
            DriverBankAccount(
                driver_bank_account_id=301,
                driver_id=10,
                bank_code="001",
                agency="1234",
                account="98765",
                account_digit="1",
                account_type=DriverBankAccountType.CHECKING,
                pix_key_type=DriverPixKeyType.CPF,
                pix_key="12345678901",
                is_primary=True,
                created_at=NOW,
                created_by=7,
            ),
        ),
    )


def make_registration():
    return parse_driver_registration(
        name="Corrigido",
        cpf="987.654.321-00",
        rg="RG2",
        birth_date_text="02/02/1982",
        cnh_number="CNH2",
        cnh_category="E",
        cnh_expiration_date_text="03/03/2033",
        phone="41988887777",
        email="new@example.com",
        postal_code="01001000",
        street="Praça da Sé",
        number="10",
        complement="Sala 1",
        district="Sé",
        city="São Paulo",
        state="SP",
        bank_code="341",
        agency="4321",
        account="12345",
        account_digit="9",
        account_type_label="Conta poupança",
    )


class DriverEditInputsTests(unittest.TestCase):

    def test_builds_updated_master_data(self):
        result = build_driver_update_form_data(
            make_driver(),
            make_registration(),
            DriverStatus.INACTIVE,
        )
        self.assertEqual(result.driver_id, 10)
        self.assertEqual(result.name, "Corrigido")
        self.assertEqual(result.cpf, "987.654.321-00")
        self.assertEqual(result.cnh_category, "E")
        self.assertEqual(result.status, DriverStatus.INACTIVE)

    def test_preserves_primary_child_ids_and_creation_audit(self):
        result = build_driver_update_form_data(
            make_driver(),
            make_registration(),
            DriverStatus.ACTIVE,
        )
        self.assertEqual(result.contacts[0].driver_contact_id, 101)
        self.assertEqual(result.contacts[0].created_at, NOW)
        self.assertEqual(result.contacts[0].created_by, 7)
        self.assertEqual(result.addresses[0].driver_address_id, 201)
        self.assertEqual(result.bank_accounts[0].driver_bank_account_id, 301)

    def test_preserves_unedited_contact_and_bank_fields(self):
        result = build_driver_update_form_data(
            make_driver(),
            make_registration(),
            DriverStatus.ACTIVE,
        )
        self.assertEqual(
            result.contacts[0].secondary_phone,
            "4133334444",
        )
        self.assertEqual(
            result.bank_accounts[0].pix_key_type,
            DriverPixKeyType.CPF,
        )
        self.assertEqual(
            result.bank_accounts[0].pix_key,
            "12345678901",
        )

    def test_preserves_non_primary_children(self):
        driver = make_driver()
        result = build_driver_update_form_data(
            driver,
            make_registration(),
            DriverStatus.ACTIVE,
        )
        self.assertEqual(result.contacts[1], driver.contacts[1])

    def test_rejects_non_persisted_driver(self):
        driver = make_driver()
        driver = Driver(
            name=driver.name,
            cpf=driver.cpf,
            rg=driver.rg,
            birth_date=driver.birth_date,
            cnh_number=driver.cnh_number,
            cnh_category=driver.cnh_category,
            cnh_expiration_date=driver.cnh_expiration_date,
            status=driver.status,
            contacts=driver.contacts,
            addresses=driver.addresses,
            bank_accounts=driver.bank_accounts,
        )
        with self.assertRaises(ValueError):
            build_driver_update_form_data(
                driver,
                make_registration(),
                DriverStatus.ACTIVE,
            )


if __name__ == "__main__":
    unittest.main()
