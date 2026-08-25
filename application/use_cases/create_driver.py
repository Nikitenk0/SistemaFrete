from datetime import date

from application.exceptions import (
    DriverAlreadyExistsError,
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


class CreateDriver:

    def __init__(
        self,
        unit_of_work_factory: DriverUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
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
        status: DriverStatus = DriverStatus.ACTIVE,
        created_by: int | None = None
    ) -> Driver:

        try:
            driver = Driver(
                name=name,
                cpf=cpf,
                rg=rg,
                birth_date=birth_date,
                cnh_number=cnh_number,
                cnh_category=cnh_category,
                cnh_expiration_date=(
                    cnh_expiration_date
                ),
                status=status,
                contacts=contacts,
                addresses=addresses,
                bank_accounts=bank_accounts,
                created_by=created_by,
                updated_by=created_by
            )
        except ValueError as error:
            raise InvalidDriverDataError(
                str(error)
            ) from error

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            existing_driver = (
                unit_of_work.drivers.get_by_cpf(
                    driver.cpf
                )
            )

            if existing_driver is not None:
                raise DriverAlreadyExistsError(
                    "CPF já cadastrado para outro motorista"
                )

            created_driver = (
                unit_of_work.drivers.add(
                    driver
                )
            )

            unit_of_work.commit()

            return created_driver
