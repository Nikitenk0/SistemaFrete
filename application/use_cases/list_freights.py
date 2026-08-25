from datetime import datetime

from application.dtos.freight_query import (
    FreightListItem,
    FreightQueryFilters,
)
from application.exceptions import InvalidFreightDataError
from application.ports.freight_query_repository import (
    FreightQueryRepository,
)
from domain.models.freight import FreightStatus


class ListFreights:

    def __init__(
        self,
        repository: FreightQueryRepository,
    ):
        self._repository = repository

    def execute(
        self,
        *,
        customer_id: int | None = None,
        status: FreightStatus | None = None,
        completed_from: datetime | None = None,
        completed_to: datetime | None = None,
    ) -> tuple[FreightListItem, ...]:

        self._validate_filters(
            customer_id=customer_id,
            status=status,
            completed_from=completed_from,
            completed_to=completed_to,
        )

        filters = FreightQueryFilters(
            customer_id=customer_id,
            status=status,
            completed_from=completed_from,
            completed_to=completed_to,
        )

        return self._repository.list(
            filters
        )

    @staticmethod
    def _validate_filters(
        *,
        customer_id: int | None,
        status: FreightStatus | None,
        completed_from: datetime | None,
        completed_to: datetime | None,
    ) -> None:

        if (
            customer_id is not None
            and customer_id < 1
        ):
            raise InvalidFreightDataError(
                "customer_id inválido"
            )

        if (
            completed_from is not None
            and completed_to is not None
            and completed_to < completed_from
        ):
            raise InvalidFreightDataError(
                "Período de conclusão inválido"
            )

        has_completion_period = (
            completed_from is not None
            or completed_to is not None
        )

        if (
            has_completion_period
            and status is not None
            and status != FreightStatus.COMPLETED
        ):
            raise InvalidFreightDataError(
                "Filtro por período de conclusão exige "
                "status COMPLETED ou nenhum status"
            )
