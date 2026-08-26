from application.exceptions import (
    InvalidTransportProviderDataError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
)


class SearchTransportProviders:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        query: str = "",
        status: TransportProviderStatus | None = None,
        provider_type: TransportProviderType | None = None,
        limit: int = 100,
    ) -> tuple[TransportProvider, ...]:
        if not isinstance(query, str):
            raise InvalidTransportProviderDataError(
                "query inválida"
            )

        if limit < 1 or limit > 200:
            raise InvalidTransportProviderDataError(
                "limit inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:
            return unit_of_work.providers.search(
                query=query.strip(),
                status=status,
                provider_type=provider_type,
                limit=limit,
            )
