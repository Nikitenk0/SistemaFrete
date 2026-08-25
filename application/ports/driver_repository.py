from typing import Protocol

from domain.models.driver import (
    Driver
)


class DriverRepository(Protocol):

    def add(
        self,
        driver: Driver
    ) -> Driver:
        ...

    def get_by_id(
        self,
        driver_id: int
    ) -> Driver | None:
        ...

    def get_by_cpf(
        self,
        cpf: str
    ) -> Driver | None:
        ...

    def search(
        self,
        query: str,
        limit: int = 20
    ) -> tuple[Driver, ...]:
        ...
