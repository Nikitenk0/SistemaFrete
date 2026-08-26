from datetime import datetime, timezone

from application.exceptions import (
    InvalidTransportProviderDataError,
    TransportProviderAlreadyExistsError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
)


class CreateTransportProvider:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        legal_name: str,
        tax_document: str,
        provider_type: TransportProviderType,
        trade_name: str | None = None,
        status: TransportProviderStatus = TransportProviderStatus.ACTIVE,
        created_by: int | None = None,
    ) -> TransportProvider:
        if created_by is not None and created_by < 1:
            raise InvalidTransportProviderDataError(
                "created_by inválido"
            )

        try:
            provider = TransportProvider(
                legal_name=legal_name,
                trade_name=trade_name,
                tax_document=tax_document,
                provider_type=provider_type,
                status=status,
                created_at=datetime.now(timezone.utc),
                created_by=created_by,
                updated_at=datetime.now(timezone.utc),
                updated_by=created_by,
            )
        except (TypeError, ValueError) as error:
            raise InvalidTransportProviderDataError(
                str(error)
            ) from error

        with self._unit_of_work_factory.create() as unit_of_work:
            if (
                unit_of_work.providers.get_by_tax_document(
                    provider.tax_document
                )
                is not None
            ):
                raise TransportProviderAlreadyExistsError(
                    "Documento já cadastrado para outro prestador"
                )

            created = unit_of_work.providers.add(
                provider
            )
            unit_of_work.commit()
            return created
