from application.dtos.driver_query import (
    DriverListItem
)
from application.exceptions import (
    InvalidDriverDataError
)
from application.ports.driver_query_repository import (
    DriverQueryRepository
)
from domain.models.driver import (
    DriverStatus
)


class ListDrivers:

    def __init__(
        self,
        repository: DriverQueryRepository
    ):
        self._repository = repository

    def execute(
        self,
        query: str = "",
        status: DriverStatus | None = None,
        limit: int = 100
    ) -> tuple[DriverListItem, ...]:

        if limit < 1 or limit > 200:
            raise InvalidDriverDataError(
                "limit inválido"
            )

        try:
            normalized_status = (
                DriverStatus(status)
                if status is not None
                else None
            )
        except (ValueError, TypeError) as error:
            raise InvalidDriverDataError(
                "status inválido"
            ) from error

        normalized_query = query.strip()

        return self._repository.list(
            query=normalized_query,
            status=normalized_status,
            limit=limit
        )
