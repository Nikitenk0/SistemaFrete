from application.ports.customer_unit_of_work import (
    CustomerUnitOfWorkFactory
)
from domain.models.customer import (
    Customer
)


class SearchCustomers:

    def __init__(
        self,
        unit_of_work_factory: CustomerUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        query: str,
        limit: int = 20
    ) -> tuple[Customer, ...]:

        query = query.strip()

        if not query:
            return ()

        if limit < 1:
            return ()

        limit = min(
            limit,
            100
        )

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            return (
                unit_of_work.customers.search(
                    query=query,
                    limit=limit
                )
            )