from application.exceptions import (
    CustomerAlreadyExistsError,
    InvalidCustomerDataError
)
from application.ports.customer_unit_of_work import (
    CustomerUnitOfWorkFactory
)
from domain.models.customer import (
    Customer,
    CustomerPersonType,
    CustomerStatus
)
from domain.models.customer_address import (
    CustomerAddress
)
from domain.models.customer_contact import (
    CustomerContact
)
from domain.models.customer_operational_location import (
    CustomerOperationalLocation
)


class CreateCustomer:

    def __init__(
        self,
        unit_of_work_factory: CustomerUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        person_type: CustomerPersonType,
        document: str,
        legal_name: str | None = None,
        trade_name: str | None = None,
        state_registration: str | None = None,
        status: CustomerStatus = (
            CustomerStatus.ACTIVE
        ),
        general_observation: str | None = None,
        customer_group_id: int | None = None,
        contacts: tuple[
            CustomerContact,
            ...
        ] = (),
        addresses: tuple[
            CustomerAddress,
            ...
        ] = (),
        operational_locations: tuple[
            CustomerOperationalLocation,
            ...
        ] = (),
        created_by: int | None = None
    ) -> Customer:

        try:

            customer = Customer(
                person_type=person_type,
                document=document,
                legal_name=legal_name,
                trade_name=trade_name,
                state_registration=(
                    state_registration
                ),
                status=status,
                general_observation=(
                    general_observation
                ),
                customer_group_id=(
                    customer_group_id
                ),
                contacts=contacts,
                addresses=addresses,
                operational_locations=(
                    operational_locations
                ),
                created_by=created_by,
                updated_by=created_by
            )

        except ValueError as error:

            raise InvalidCustomerDataError(
                str(error)
            ) from error

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            existing_customer = (
                unit_of_work.customers
                .get_by_document(
                    customer.document
                )
            )

            if existing_customer is not None:
                raise CustomerAlreadyExistsError(
                    "CPF/CNPJ já cadastrado"
                )

            created_customer = (
                unit_of_work.customers.add(
                    customer
                )
            )

            unit_of_work.commit()

            return created_customer