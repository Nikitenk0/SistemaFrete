from typing import Protocol

from domain.models.customer import (
    Customer
)


class CustomerRepository(Protocol):

    def add(
        self,
        customer: Customer
    ) -> Customer:
        ...

    def get_by_id(
        self,
        customer_id: int
    ) -> Customer | None:
        ...

    def get_by_document(
        self,
        document: str
    ) -> Customer | None:
        ...

    def search(
        self,
        query: str,
        limit: int = 20
    ) -> tuple[Customer, ...]:
        ...