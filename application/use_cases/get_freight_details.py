from application.dtos.freight_query import FreightDetails
from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
)
from application.ports.freight_query_repository import (
    FreightQueryRepository,
)


class GetFreightDetails:

    def __init__(
        self,
        repository: FreightQueryRepository,
    ):
        self._repository = repository

    def execute(
        self,
        freight_id: int,
    ) -> FreightDetails:

        if freight_id < 1:
            raise InvalidFreightDataError(
                "freight_id inválido"
            )

        result = self._repository.get_by_id(
            freight_id
        )

        if result is None:
            raise FreightNotFoundError(
                "Frete não encontrado"
            )

        return result
