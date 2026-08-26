from application.dtos.freight_driver_selection import (
    FreightDriverSelectionItem,
)
from application.exceptions import InvalidDriverDataError
from application.ports.freight_driver_selection_repository import (
    FreightDriverSelectionRepository,
)


class SearchAvailableFreightDrivers:

    def __init__(
        self,
        repository: FreightDriverSelectionRepository,
    ):
        self._repository = repository

    def execute(
        self,
        query: str,
        limit: int = 20,
    ) -> tuple[FreightDriverSelectionItem, ...]:

        if not isinstance(query, str):
            raise InvalidDriverDataError(
                "query inválida"
            )

        normalized_query = query.strip()

        if not normalized_query:
            return ()

        if limit < 1 or limit > 100:
            raise InvalidDriverDataError(
                "limit inválido"
            )

        return self._repository.search_available(
            normalized_query,
            limit=limit,
        )
