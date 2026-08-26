import unittest

from domain.models.driver_bank_account import DriverBankAccountType
from presentation.desktop.driver_registration_inputs import (
    parse_driver_registration,
)


class DriverRegistrationInputsTests(unittest.TestCase):

    def _valid(self, **changes):
        values = dict(
            name="João da Silva",
            cpf="123.456.789-09",
            rg="1234567",
            birth_date_text="10/05/1985",
            cnh_number="99887766",
            cnh_category="E",
            cnh_expiration_date_text="10/05/2030",
            phone="(41) 99999-0000",
            email="JOAO@EXEMPLO.COM",
            postal_code="80000-000",
            street="Rua Teste",
            number="123",
            complement="Apto 4",
            district="Centro",
            city="Curitiba",
            state="pr",
            bank_code="001",
            agency="1234",
            account="98765",
            account_digit="1",
            account_type_label="Conta corrente",
        )
        values.update(changes)
        return values

    def test_builds_minimum_valid_driver_registration(self):
        result = parse_driver_registration(**self._valid())

        self.assertEqual(result.name, "João da Silva")
        self.assertEqual(result.birth_date.isoformat(), "1985-05-10")
        self.assertEqual(len(result.contacts), 1)
        self.assertTrue(result.contacts[0].is_primary)
        self.assertEqual(result.contacts[0].phone, "41999990000")
        self.assertEqual(result.contacts[0].email, "joao@exemplo.com")
        self.assertEqual(len(result.addresses), 1)
        self.assertTrue(result.addresses[0].is_primary)
        self.assertEqual(result.addresses[0].postal_code, "80000000")
        self.assertEqual(result.addresses[0].state, "PR")
        self.assertEqual(len(result.bank_accounts), 1)
        self.assertTrue(result.bank_accounts[0].is_primary)
        self.assertEqual(
            result.bank_accounts[0].account_type,
            DriverBankAccountType.CHECKING,
        )

    def test_accepts_optional_email_complement_and_digit_empty(self):
        result = parse_driver_registration(
            **self._valid(email="", complement="", account_digit="")
        )
        self.assertIsNone(result.contacts[0].email)
        self.assertIsNone(result.addresses[0].complement)
        self.assertIsNone(result.bank_accounts[0].account_digit)

    def test_rejects_invalid_birth_date_format(self):
        with self.assertRaisesRegex(ValueError, "DD/MM/AAAA"):
            parse_driver_registration(
                **self._valid(birth_date_text="1985-05-10")
            )

    def test_rejects_invalid_phone(self):
        with self.assertRaisesRegex(ValueError, "phone inválido"):
            parse_driver_registration(**self._valid(phone="123"))

    def test_rejects_invalid_postal_code(self):
        with self.assertRaisesRegex(ValueError, "postal_code inválido"):
            parse_driver_registration(**self._valid(postal_code="123"))

    def test_rejects_invalid_bank_code(self):
        with self.assertRaisesRegex(ValueError, "bank_code inválido"):
            parse_driver_registration(**self._valid(bank_code="1"))

    def test_rejects_unknown_account_type(self):
        with self.assertRaisesRegex(ValueError, "Tipo de conta"):
            parse_driver_registration(
                **self._valid(account_type_label="Outro")
            )


if __name__ == "__main__":
    unittest.main()
