from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    InvalidTransportProviderDataError,
    TransportProviderAlreadyExistsError,
    TransportProviderNotFoundError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
    normalize_transport_provider_document,
)


class UpdateTransportProvider:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        transport_provider_id: int,
        legal_name: str,
        tax_document: str,
        provider_type: TransportProviderType,
        trade_name: str | None = None,
        status: TransportProviderStatus = TransportProviderStatus.ACTIVE,
        updated_by: int | None = None,
    ) -> TransportProvider:
        if transport_provider_id < 1:
            raise InvalidTransportProviderDataError(
                "transport_provider_id inválido"
            )

        if updated_by is not None and updated_by < 1:
            raise InvalidTransportProviderDataError(
                "updated_by inválido"
            )

        try:
            normalized_document = (
                normalize_transport_provider_document(
                    tax_document
                )
            )
        except ValueError as error:
            raise InvalidTransportProviderDataError(
                str(error)
            ) from error

        with self._unit_of_work_factory.create() as unit_of_work:
            current = unit_of_work.providers.get_by_id_for_update(
                transport_provider_id
            )

            if current is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte não encontrado"
                )

            duplicate = unit_of_work.providers.get_by_tax_document(
                normalized_document
            )
            if (
                duplicate is not None
                and duplicate.transport_provider_id
                != transport_provider_id
            ):
                raise TransportProviderAlreadyExistsError(
                    "Documento já cadastrado para outro prestador"
                )

            try:
                updated = replace(
                    current,
                    legal_name=legal_name,
                    trade_name=trade_name,
                    tax_document=normalized_document,
                    provider_type=provider_type,
                    status=status,
                    updated_at=datetime.now(timezone.utc),
                    updated_by=updated_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidTransportProviderDataError(
                    str(error)
                ) from error

            saved = unit_of_work.providers.save(
                updated
            )
            unit_of_work.commit()
            return saved
