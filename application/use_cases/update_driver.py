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
from application.ports.driver_unit_of_work import (
    DriverUnitOfWorkFactory
)
from domain.models.driver import (
    Driver,
    DriverStatus
)
from domain.models.driver_address import (
    DriverAddress
)
from domain.models.driver_bank_account import (
    DriverBankAccount
)
from domain.models.driver_contact import (
    DriverContact
)


class UpdateDriver:

    def __init__(
        self,
        unit_of_work_factory: DriverUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        driver_id: int,
        name: str,
        cpf: str,
        rg: str,
        birth_date: date,
        cnh_number: str,
        cnh_category: str,
        cnh_expiration_date: date,
        contacts: tuple[DriverContact, ...],
        addresses: tuple[DriverAddress, ...],
        bank_accounts: tuple[DriverBankAccount, ...],
        status: DriverStatus,
        updated_by: int | None = None
    ) -> Driver:

        if driver_id < 1:
            raise InvalidDriverDataError(
                "driver_id inválido"
            )

        if updated_by is not None and updated_by < 1:
            raise InvalidDriverDataError(
                "updated_by inválido"
            )

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            current_driver = (
                unit_of_work.drivers.get_by_id_for_update(
                    driver_id
                )
            )

            if current_driver is None:
                raise DriverNotFoundError(
                    "Motorista não encontrado"
                )

            now = datetime.now(
                timezone.utc
            )

            try:
                prepared_contacts = tuple(
                    self._prepare_contact(
                        contact,
                        driver_id,
                        now,
                        updated_by
                    )
                    for contact in contacts
                )
                prepared_addresses = tuple(
                    self._prepare_address(
                        address,
                        driver_id,
                        now,
                        updated_by
                    )
                    for address in addresses
                )
                prepared_bank_accounts = tuple(
                    self._prepare_bank_account(
                        bank_account,
                        driver_id,
                        now,
                        updated_by
                    )
                    for bank_account in bank_accounts
                )

                self._validate_unique_child_ids(
                    prepared_contacts,
                    "driver_contact_id"
                )
                self._validate_unique_child_ids(
                    prepared_addresses,
                    "driver_address_id"
                )
                self._validate_unique_child_ids(
                    prepared_bank_accounts,
                    "driver_bank_account_id"
                )

                updated_driver = Driver(
                    driver_id=driver_id,
                    name=name,
                    cpf=cpf,
                    rg=rg,
                    birth_date=birth_date,
                    cnh_number=cnh_number,
                    cnh_category=cnh_category,
                    cnh_expiration_date=(
                        cnh_expiration_date
                    ),
                    status=DriverStatus(
                        status
                    ),
                    contacts=prepared_contacts,
                    addresses=prepared_addresses,
                    bank_accounts=(
                        prepared_bank_accounts
                    ),
                    created_at=current_driver.created_at,
                    created_by=current_driver.created_by,
                    updated_at=now,
                    updated_by=updated_by
                )

            except (ValueError, TypeError) as error:
                raise InvalidDriverDataError(
                    str(error)
                ) from error

            driver_with_cpf = (
                unit_of_work.drivers.get_by_cpf(
                    updated_driver.cpf
                )
            )

            if (
                driver_with_cpf is not None
                and driver_with_cpf.driver_id
                != driver_id
            ):
                raise DriverAlreadyExistsError(
                    "CPF já cadastrado para outro motorista"
                )

            saved_driver = (
                unit_of_work.drivers.save(
                    updated_driver
                )
            )

            unit_of_work.commit()

            return saved_driver

    @staticmethod
    def _prepare_contact(
        contact: DriverContact,
        driver_id: int,
        now: datetime,
        updated_by: int | None
    ) -> DriverContact:

        if contact.driver_id not in {
            None,
            driver_id
        }:
            raise ValueError(
                "Contato não pertence ao motorista"
            )

        is_new = (
            contact.driver_contact_id is None
        )

        return replace(
            contact,
            driver_id=driver_id,
            created_by=(
                updated_by
                if is_new
                else contact.created_by
            ),
            updated_at=now,
            updated_by=updated_by
        )

    @staticmethod
    def _prepare_address(
        address: DriverAddress,
        driver_id: int,
        now: datetime,
        updated_by: int | None
    ) -> DriverAddress:

        if address.driver_id not in {
            None,
            driver_id
        }:
            raise ValueError(
                "Endereço não pertence ao motorista"
            )

        is_new = (
            address.driver_address_id is None
        )

        return replace(
            address,
            driver_id=driver_id,
            created_by=(
                updated_by
                if is_new
                else address.created_by
            ),
            updated_at=now,
            updated_by=updated_by
        )

    @staticmethod
    def _prepare_bank_account(
        bank_account: DriverBankAccount,
        driver_id: int,
        now: datetime,
        updated_by: int | None
    ) -> DriverBankAccount:

        if bank_account.driver_id not in {
            None,
            driver_id
        }:
            raise ValueError(
                "Conta bancária não pertence ao motorista"
            )

        is_new = (
            bank_account.driver_bank_account_id
            is None
        )

        return replace(
            bank_account,
            driver_id=driver_id,
            created_by=(
                updated_by
                if is_new
                else bank_account.created_by
            ),
            updated_at=now,
            updated_by=updated_by
        )

    @staticmethod
    def _validate_unique_child_ids(
        items: tuple,
        id_attribute: str
    ) -> None:

        identifiers = [
            getattr(
                item,
                id_attribute
            )
            for item in items
            if getattr(
                item,
                id_attribute
            ) is not None
        ]

        if len(identifiers) != len(set(identifiers)):
            raise ValueError(
                f"{id_attribute} duplicado"
            )
