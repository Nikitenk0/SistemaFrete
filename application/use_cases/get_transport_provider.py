from application.exceptions import (
    InvalidTransportProviderDataError,
    TransportProviderNotFoundError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.transport_provider import (
    TransportProvider,
)


class GetTransportProvider:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        transport_provider_id: int,
    ) -> TransportProvider:
        if transport_provider_id < 1:
            raise InvalidTransportProviderDataError(
                "transport_provider_id inválido"
            )

        with self._unit_of_work_factory.create() as unit_of_work:
            provider = unit_of_work.providers.get_by_id(
                transport_provider_id
            )

            if provider is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte não encontrado"
                )

            return provider
