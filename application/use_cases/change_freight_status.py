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
from domain.freight_lifecycle import (
    transition_freight
)
from domain.freight_operational_readiness import (
    validate_freight_operational_readiness
)
from domain.models.freight import (
    Freight,
    FreightStatus
)


class ChangeFreightStatus:

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
        target_status: FreightStatus,
        user_id: int | None = None,
        observation: str | None = None
    ) -> Freight:

        if freight_id < 1:
            raise InvalidFreightDataError(
                "freight_id inválido"
            )

        if (
            user_id is not None
            and user_id < 1
        ):
            raise InvalidFreightDataError(
                "user_id inválido"
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

            if target_status == FreightStatus.IN_PROGRESS:
                try:
                    validate_freight_operational_readiness(
                        transport_units=(
                            unit_of_work.transport_units
                            .list_by_freight_id(
                                freight_id
                            )
                        ),
                        active_driver_assignments=(
                            unit_of_work.driver_assignments
                            .list_active_by_freight_id(
                                freight_id
                            )
                        ),
                        vehicle_records=(
                            unit_of_work.vehicle_records
                            .list_by_freight_id(
                                freight_id
                            )
                        )
                    )
                except ValueError as error:
                    raise InvalidFreightStateError(
                        str(error)
                    ) from error

            try:
                updated_freight = transition_freight(
                    freight=freight,
                    target_status=target_status,
                    occurred_at=datetime.now(
                        timezone.utc
                    ),
                    user_id=user_id,
                    observation=observation
                )
            except ValueError as error:
                raise InvalidFreightStateError(
                    str(error)
                ) from error

            saved_freight = (
                unit_of_work.freights.save(
                    updated_freight
                )
            )

            unit_of_work.commit()

            return saved_freight
