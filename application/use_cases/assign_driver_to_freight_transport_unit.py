from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    DriverNotFoundError,
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidDriverStateError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.ports.freight_driver_assignment_unit_of_work import (
    FreightDriverAssignmentUnitOfWorkFactory
)
from domain.models.driver import (
    DriverStatus
)
from domain.models.freight import (
    FreightStatus
)
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)


class AssignDriverToFreightTransportUnit:

    def __init__(
        self,
        unit_of_work_factory:
            FreightDriverAssignmentUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        freight_transport_unit_id: int,
        driver_id: int,
        started_at: datetime | None = None,
        created_by: int | None = None
    ) -> FreightDriverAssignment:

        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError(
                "freight_transport_unit_id inválido"
            )

        if driver_id < 1:
            raise InvalidFreightDataError(
                "driver_id inválido"
            )

        if created_by is not None and created_by < 1:
            raise InvalidFreightDataError(
                "created_by inválido"
            )

        now = datetime.now(
            timezone.utc
        )

        if started_at is None:
            started_at = now

        with self._unit_of_work_factory.create() as unit_of_work:

            transport_unit = (
                unit_of_work.transport_units.get_by_id(
                    freight_transport_unit_id
                )
            )

            if transport_unit is None:
                raise FreightTransportUnitNotFoundError(
                    "Unidade de transporte não encontrada"
                )

            freight = (
                unit_of_work.freights.get_by_id_for_update(
                    transport_unit.freight_id
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
                    "Frete concluído ou cancelado não aceita "
                    "nova participação de motorista"
                )

            driver = unit_of_work.drivers.get_by_id(
                driver_id
            )

            if driver is None:
                raise DriverNotFoundError(
                    "Motorista não encontrado"
                )

            if driver.status != DriverStatus.ACTIVE:
                raise InvalidDriverStateError(
                    "Motorista inativo não pode receber "
                    "nova participação operacional"
                )

            active_unit_assignment = (
                unit_of_work.driver_assignments
                .get_active_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )

            if active_unit_assignment is not None:
                raise InvalidFreightStateError(
                    "Unidade de transporte já possui "
                    "motorista ativo"
                )

            active_driver_assignment = (
                unit_of_work.driver_assignments
                .get_active_by_driver_id(
                    driver_id
                )
            )

            if active_driver_assignment is not None:
                raise InvalidFreightStateError(
                    "Motorista já possui participação "
                    "operacional ativa"
                )

            try:
                assignment = FreightDriverAssignment(
                    freight_transport_unit_id=(
                        freight_transport_unit_id
                    ),
                    driver_id=driver_id,
                    started_at=started_at,
                    created_at=now,
                    created_by=created_by,
                    updated_at=now,
                    updated_by=created_by
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_assignment = (
                unit_of_work.driver_assignments.add(
                    assignment
                )
            )

            unit_of_work.commit()

            return created_assignment
