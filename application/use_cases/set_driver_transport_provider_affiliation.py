from dataclasses import replace
from datetime import datetime, timezone

from application.exceptions import (
    DriverNotFoundError,
    InvalidDriverStateError,
    InvalidTransportProviderDataError,
    InvalidTransportProviderStateError,
    TransportProviderNotFoundError,
)
from application.ports.transport_provider_unit_of_work import (
    TransportProviderUnitOfWorkFactory,
)
from domain.models.driver import DriverStatus
from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderAffiliation,
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProviderStatus,
    TransportProviderType,
)


class SetDriverTransportProviderAffiliation:

    def __init__(
        self,
        unit_of_work_factory: TransportProviderUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        driver_id: int,
        transport_provider_id: int,
        role: DriverTransportProviderRole,
        changed_at: datetime | None = None,
        changed_by: int | None = None,
    ) -> DriverTransportProviderAffiliation:
        if driver_id < 1:
            raise InvalidTransportProviderDataError(
                "driver_id inválido"
            )

        if transport_provider_id < 1:
            raise InvalidTransportProviderDataError(
                "transport_provider_id inválido"
            )

        if changed_by is not None and changed_by < 1:
            raise InvalidTransportProviderDataError(
                "changed_by inválido"
            )

        now = changed_at or datetime.now(timezone.utc)

        with self._unit_of_work_factory.create() as unit_of_work:
            driver = unit_of_work.drivers.get_by_id_for_update(
                driver_id
            )
            if driver is None:
                raise DriverNotFoundError(
                    "Motorista não encontrado"
                )

            if driver.status != DriverStatus.ACTIVE:
                raise InvalidDriverStateError(
                    "Motorista inativo não pode receber novo vínculo"
                )

            provider = unit_of_work.providers.get_by_id_for_update(
                transport_provider_id
            )
            if provider is None:
                raise TransportProviderNotFoundError(
                    "Prestador de transporte não encontrado"
                )

            if provider.status != TransportProviderStatus.ACTIVE:
                raise InvalidTransportProviderStateError(
                    "Prestador inativo não pode receber novo vínculo"
                )

            try:
                role = DriverTransportProviderRole(
                    role
                )
            except (TypeError, ValueError) as error:
                raise InvalidTransportProviderDataError(
                    "role inválido"
                ) from error

            if (
                provider.provider_type
                == TransportProviderType.INDIVIDUAL
                and role == DriverTransportProviderRole.OWNER
                and provider.tax_document != driver.cpf
            ):
                raise InvalidTransportProviderDataError(
                    "Prestador pessoa física OWNER deve possuir "
                    "o mesmo CPF do motorista"
                )

            current = (
                unit_of_work.driver_affiliations
                .get_active_by_driver_id(
                    driver_id
                )
            )

            if (
                current is not None
                and current.transport_provider_id
                == transport_provider_id
                and current.role == role
            ):
                return current

            if current is not None:
                ended = replace(
                    current,
                    ended_at=now,
                    updated_at=now,
                    updated_by=changed_by,
                )
                unit_of_work.driver_affiliations.save(
                    ended
                )

            try:
                affiliation = DriverTransportProviderAffiliation(
                    driver_id=driver_id,
                    transport_provider_id=transport_provider_id,
                    role=role,
                    started_at=now,
                    created_at=now,
                    created_by=changed_by,
                    updated_at=now,
                    updated_by=changed_by,
                )
            except (TypeError, ValueError) as error:
                raise InvalidTransportProviderDataError(
                    str(error)
                ) from error

            created = unit_of_work.driver_affiliations.add(
                affiliation
            )
            unit_of_work.commit()
            return created
