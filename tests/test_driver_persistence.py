import unittest
from datetime import (
    date,
    datetime,
    timezone
)

from domain.models.driver import (
    Driver,
    DriverStatus
)
from domain.models.driver_address import (
    DriverAddress,
    DriverAddressType
)
from domain.models.driver_bank_account import (
    DriverBankAccount,
    DriverBankAccountType,
    DriverPixKeyType
)
from domain.models.driver_contact import (
    DriverContact
)
from infrastructure.persistence.sqlalchemy.base import (
    Base
)
import infrastructure.persistence.sqlalchemy.models  # noqa: F401
from infrastructure.persistence.sqlalchemy.driver_repository import (
    SqlAlchemyDriverRepository
)
from infrastructure.persistence.sqlalchemy.driver_unit_of_work import (
    SqlAlchemyDriverUnitOfWork
)
from infrastructure.persistence.sqlalchemy.models import (
    DriverAddressModel,
    DriverBankAccountModel,
    DriverContactModel,
    DriverModel
)


NOW = datetime(
    2026,
    8,
    24,
    21,
    30,
    tzinfo=timezone.utc
)


def build_driver() -> Driver:

    return Driver(
        name="Joao da Silva",
        cpf="123.456.789-01",
        rg="12.345.678-9",
        birth_date=date(1985, 5, 10),
        cnh_number="12345678901",
        cnh_category="E",
        cnh_expiration_date=date(2030, 5, 10),
        contacts=(
            DriverContact(
                phone="11999999999",
                email="JOAO@EXAMPLE.COM",
                is_primary=True,
                created_at=NOW,
                created_by=7,
                updated_at=NOW,
                updated_by=7
            ),
        ),
        addresses=(
            DriverAddress(
                postal_code="01001-000",
                street="Praca da Se",
                number="100",
                district="Se",
                city="Sao Paulo",
                state="sp",
                address_type=(
                    DriverAddressType.RESIDENTIAL
                ),
                is_primary=True,
                created_at=NOW,
                created_by=7,
                updated_at=NOW,
                updated_by=7
            ),
        ),
        bank_accounts=(
            DriverBankAccount(
                bank_code="001",
                agency="1234",
                account="98765",
                account_digit="4",
                account_type=(
                    DriverBankAccountType.CHECKING
                ),
                pix_key_type=DriverPixKeyType.CPF,
                pix_key="12345678901",
                is_primary=True,
                created_at=NOW,
                created_by=7,
                updated_at=NOW,
                updated_by=7
            ),
        ),
        created_at=NOW,
        created_by=7,
        updated_at=NOW,
        updated_by=7
    )


class DriverPersistenceMetadataTests(
    unittest.TestCase
):

    def test_registers_driver_tables(
        self
    ) -> None:

        for table_name in (
            "drivers",
            "driver_contacts",
            "driver_addresses",
            "driver_bank_accounts"
        ):
            self.assertIn(
                table_name,
                Base.metadata.tables
            )

    def test_driver_table_has_complete_registration_fields(
        self
    ) -> None:

        table = Base.metadata.tables[
            "drivers"
        ]

        for column_name in (
            "driver_id",
            "name",
            "cpf",
            "rg",
            "birth_date",
            "cnh_number",
            "cnh_category",
            "cnh_expiration_date",
            "status",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by"
        ):
            self.assertIn(
                column_name,
                table.c
            )

        self.assertFalse(
            table.c.cpf.nullable
        )
        self.assertFalse(
            table.c.cnh_number.nullable
        )

    def test_child_tables_cascade_with_driver(
        self
    ) -> None:

        for table_name in (
            "driver_contacts",
            "driver_addresses",
            "driver_bank_accounts"
        ):
            table = Base.metadata.tables[
                table_name
            ]

            foreign_key = next(
                iter(
                    table.c.driver_id.foreign_keys
                )
            )

            self.assertEqual(
                foreign_key.target_fullname,
                "drivers.driver_id"
            )
            self.assertEqual(
                foreign_key.ondelete,
                "CASCADE"
            )

    def test_primary_records_are_protected_by_unique_indexes(
        self
    ) -> None:

        expected_indexes = {
            "driver_contacts": (
                "uq_driver_contacts_driver_primary"
            ),
            "driver_addresses": (
                "uq_driver_addresses_driver_primary"
            ),
            "driver_bank_accounts": (
                "uq_driver_bank_accounts_driver_primary"
            )
        }

        for table_name, index_name in expected_indexes.items():
            table = Base.metadata.tables[
                table_name
            ]
            indexes = {
                index.name: index
                for index in table.indexes
            }

            self.assertIn(
                index_name,
                indexes
            )
            self.assertTrue(
                indexes[index_name].unique
            )

    def test_bank_account_has_pix_pair_constraint(
        self
    ) -> None:

        table = Base.metadata.tables[
            "driver_bank_accounts"
        ]

        constraint_names = {
            constraint.name
            for constraint in table.constraints
            if constraint.__class__.__name__
            == "CheckConstraint"
        }

        self.assertIn(
            "ck_driver_bank_accounts_pix_pair",
            constraint_names
        )


class DriverRepositoryMappingTests(
    unittest.TestCase
):

    def test_maps_complete_domain_driver_to_model(
        self
    ) -> None:

        driver = build_driver()

        model = SqlAlchemyDriverRepository._to_model(
            driver
        )

        self.assertEqual(
            model.name,
            "Joao da Silva"
        )
        self.assertEqual(
            model.cpf,
            "12345678901"
        )
        self.assertEqual(
            model.cnh_category,
            "E"
        )
        self.assertEqual(
            len(model.contacts),
            1
        )
        self.assertEqual(
            len(model.addresses),
            1
        )
        self.assertEqual(
            len(model.bank_accounts),
            1
        )
        self.assertEqual(
            model.contacts[0].email,
            "joao@example.com"
        )
        self.assertEqual(
            model.addresses[0].postal_code,
            "01001000"
        )
        self.assertEqual(
            model.bank_accounts[0].pix_key_type,
            "CPF"
        )

    def test_maps_persisted_complete_driver_to_domain(
        self
    ) -> None:

        model = DriverModel(
            driver_id=31,
            name="Joao da Silva",
            cpf="12345678901",
            rg="12.345.678-9",
            birth_date=date(1985, 5, 10),
            cnh_number="12345678901",
            cnh_category="E",
            cnh_expiration_date=date(2030, 5, 10),
            status="ACTIVE",
            created_at=NOW,
            created_by=7,
            updated_at=NOW,
            updated_by=7
        )

        model.contacts = [
            DriverContactModel(
                driver_contact_id=41,
                driver_id=31,
                phone="11999999999",
                secondary_phone=None,
                email="joao@example.com",
                is_primary=True,
                created_at=NOW,
                created_by=7,
                updated_at=NOW,
                updated_by=7
            )
        ]
        model.addresses = [
            DriverAddressModel(
                driver_address_id=51,
                driver_id=31,
                address_type="RESIDENTIAL",
                postal_code="01001000",
                street="Praca da Se",
                number="100",
                complement=None,
                district="Se",
                city="Sao Paulo",
                state="SP",
                is_primary=True,
                created_at=NOW,
                created_by=7,
                updated_at=NOW,
                updated_by=7
            )
        ]
        model.bank_accounts = [
            DriverBankAccountModel(
                driver_bank_account_id=61,
                driver_id=31,
                bank_code="001",
                agency="1234",
                account="98765",
                account_digit="4",
                account_type="CHECKING",
                pix_key_type="CPF",
                pix_key="12345678901",
                is_primary=True,
                created_at=NOW,
                created_by=7,
                updated_at=NOW,
                updated_by=7
            )
        ]

        driver = SqlAlchemyDriverRepository._to_domain(
            model
        )

        self.assertEqual(
            driver.driver_id,
            31
        )
        self.assertEqual(
            driver.status,
            DriverStatus.ACTIVE
        )
        self.assertEqual(
            driver.contacts[0].driver_contact_id,
            41
        )
        self.assertEqual(
            driver.addresses[0].address_type,
            DriverAddressType.RESIDENTIAL
        )
        self.assertEqual(
            driver.bank_accounts[0].account_type,
            DriverBankAccountType.CHECKING
        )
        self.assertEqual(
            driver.bank_accounts[0].pix_key_type,
            DriverPixKeyType.CPF
        )

    def test_normalizes_cpf_for_repository_queries(
        self
    ) -> None:

        self.assertEqual(
            SqlAlchemyDriverRepository._normalize_cpf(
                "123.456.789-01"
            ),
            "12345678901"
        )


class DriverUnitOfWorkIntegrationTests(
    unittest.TestCase
):

    def test_exposes_driver_repository(
        self
    ) -> None:

        class FakeSession:
            def close(self):
                pass

            def rollback(self):
                pass

        fake_session = FakeSession()

        unit_of_work = SqlAlchemyDriverUnitOfWork(
            lambda: fake_session
        )

        with unit_of_work as active:
            self.assertIsInstance(
                active.drivers,
                SqlAlchemyDriverRepository
            )


if __name__ == "__main__":
    unittest.main()
