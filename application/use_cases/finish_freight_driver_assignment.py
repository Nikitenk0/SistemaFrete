from dataclasses import replace
from datetime import (
    datetime,
    timezone
)
from decimal import Decimal

from application.exceptions import (
    FreightDriverAssignmentNotFoundError,
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.ports.freight_driver_assignment_unit_of_work import (
    FreightDriverAssignmentUnitOfWorkFactory
)
from domain.models.freight import (
    FreightStatus
)
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)


class FinishFreightDriverAssignment:

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
        freight_driver_assignment_id: int,
        actual_driver_amount: Decimal,
        ended_at: datetime | None = None,
        updated_by: int | None = None
    ) -> FreightDriverAssignment:

        if freight_driver_assignment_id < 1:
            raise InvalidFreightDataError(
                "freight_driver_assignment_id inválido"
            )

        if updated_by is not None and updated_by < 1:
            raise InvalidFreightDataError(
                "updated_by inválido"
            )

        now = datetime.now(
            timezone.utc
        )

        if ended_at is None:
            ended_at = now

        with self._unit_of_work_factory.create() as unit_of_work:

            current_assignment = (
                unit_of_work.driver_assignments.get_by_id(
                    freight_driver_assignment_id
                )
            )

            if current_assignment is None:
                raise FreightDriverAssignmentNotFoundError(
                    "Participação de motorista não encontrada"
                )

            transport_unit = (
                unit_of_work.transport_units.get_by_id(
                    current_assignment.freight_transport_unit_id
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

            if freight.current_status != FreightStatus.IN_PROGRESS:
                raise InvalidFreightStateError(
                    "Somente frete em andamento aceita "
                    "encerramento de motorista"
                )

            current_assignment = (
                unit_of_work.driver_assignments.get_by_id(
                    freight_driver_assignment_id
                )
            )

            if current_assignment is None:
                raise FreightDriverAssignmentNotFoundError(
                    "Participação de motorista não encontrada"
                )

            if not current_assignment.is_active:
                raise InvalidFreightStateError(
                    "Participação de motorista já está encerrada"
                )

            try:
                finished_assignment = replace(
                    current_assignment,
                    ended_at=ended_at,
                    actual_driver_amount=actual_driver_amount,
                    updated_at=now,
                    updated_by=updated_by
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            saved_assignment = (
                unit_of_work.driver_assignments.save(
                    finished_assignment
                )
            )

            unit_of_work.commit()

            return saved_assignment
