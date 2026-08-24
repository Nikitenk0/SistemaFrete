from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.ports.freight_unit_of_work import (
    FreightUnitOfWorkFactory
)
from domain.models.freight import (
    FreightStatus
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)


class AddFreightTransportUnit:

    def __init__(
        self,
        freight_unit_of_work_factory:
            FreightUnitOfWorkFactory
    ):
        self._freight_unit_of_work_factory = (
            freight_unit_of_work_factory
        )

    def execute(
        self,
        freight_id: int,
        created_by: int | None = None
    ) -> FreightTransportUnit:

        if freight_id < 1:
            raise InvalidFreightDataError(
                "freight_id inválido"
            )

        if (
            created_by is not None
            and created_by < 1
        ):
            raise InvalidFreightDataError(
                "created_by inválido"
            )

        with (
            self._freight_unit_of_work_factory.create()
            as unit_of_work
        ):

            freight = (
                unit_of_work.freights
                .get_by_id_for_update(
                    freight_id
                )
            )

            if freight is None:
                raise FreightNotFoundError(
                    "Frete não encontrado"
                )

            if freight.current_status not in {
                FreightStatus.PENDING,
                FreightStatus.IN_PROGRESS
            }:
                raise InvalidFreightStateError(
                    "Frete concluído ou cancelado não "
                    "aceita novas unidades de transporte"
                )

            existing_units = (
                unit_of_work.transport_units
                .list_by_freight_id(
                    freight_id
                )
            )

            next_position = (
                max(
                    (
                        unit.position
                        for unit in existing_units
                    ),
                    default=0
                )
                + 1
            )

            try:
                transport_unit = FreightTransportUnit(
                    freight_id=freight_id,
                    position=next_position,
                    created_at=datetime.now(
                        timezone.utc
                    ),
                    created_by=created_by
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_unit = (
                unit_of_work.transport_units.add(
                    transport_unit
                )
            )

            unit_of_work.commit()

            return created_unit
