from application.exceptions import (
    CustomerNotFoundError
)
from application.ports.customer_unit_of_work import (
    CustomerUnitOfWorkFactory
)
from domain.models.customer import (
    Customer
)


class GetCustomer:

    def __init__(
        self,
        unit_of_work_factory: CustomerUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        customer_id: int
    ) -> Customer:

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            customer = (
                unit_of_work.customers
                .get_by_id(
                    customer_id
                )
            )

            if customer is None:
                raise CustomerNotFoundError(
                    "Cliente não encontrado"
                )

            return customer