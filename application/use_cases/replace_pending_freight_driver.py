from datetime import datetime, timezone

from application.exceptions import (
    DriverNotFoundError,
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidDriverStateError,
    InvalidFreightDataError,
    InvalidFreightStateError,
)
from application.ports.freight_driver_assignment_unit_of_work import (
    FreightDriverAssignmentUnitOfWorkFactory,
)
from domain.models.driver import DriverStatus
from domain.models.freight import FreightStatus
from domain.models.freight_driver_assignment import FreightDriverAssignment


class ReplacePendingFreightDriver:

    def __init__(self, unit_of_work_factory: FreightDriverAssignmentUnitOfWorkFactory):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_transport_unit_id: int,
        driver_id: int,
        changed_by: int | None = None,
    ) -> FreightDriverAssignment:
        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError("freight_transport_unit_id inválido")
        if driver_id < 1:
            raise InvalidFreightDataError("driver_id inválido")
        if changed_by is not None and changed_by < 1:
            raise InvalidFreightDataError("changed_by inválido")

        now = datetime.now(timezone.utc)
        with self._unit_of_work_factory.create() as unit_of_work:
            transport_unit = unit_of_work.transport_units.get_by_id(
                freight_transport_unit_id
            )
            if transport_unit is None:
                raise FreightTransportUnitNotFoundError(
                    "Unidade de transporte não encontrada"
                )

            freight = unit_of_work.freights.get_by_id_for_update(
                transport_unit.freight_id
            )
            if freight is None:
                raise FreightNotFoundError("Frete não encontrado")
            if freight.current_status != FreightStatus.PENDING:
                raise InvalidFreightStateError(
                    "Somente frete pendente aceita troca de motorista"
                )

            current_assignment = (
                unit_of_work.driver_assignments.get_active_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )
            if current_assignment is None:
                raise InvalidFreightStateError(
                    "A unidade de transporte não possui motorista ativo para trocar"
                )
            if current_assignment.driver_id == driver_id:
                raise InvalidFreightStateError(
                    "Selecione um motorista diferente"
                )

            driver = unit_of_work.drivers.get_by_id(driver_id)
            if driver is None:
                raise DriverNotFoundError("Motorista não encontrado")
            if driver.status != DriverStatus.ACTIVE:
                raise InvalidDriverStateError(
                    "Motorista inativo não pode ser atribuído à unidade"
                )

            active_driver_assignment = (
                unit_of_work.driver_assignments.get_active_by_driver_id(driver_id)
            )
            if active_driver_assignment is not None:
                raise InvalidFreightStateError(
                    "Motorista já possui participação operacional ativa"
                )

            unit_of_work.driver_assignments.delete_by_id(
                current_assignment.freight_driver_assignment_id
            )
            replacement = FreightDriverAssignment(
                freight_transport_unit_id=freight_transport_unit_id,
                driver_id=driver_id,
                started_at=now,
                created_at=now,
                created_by=changed_by,
                updated_at=now,
                updated_by=changed_by,
            )
            created = unit_of_work.driver_assignments.add(replacement)
            unit_of_work.commit()
            return created
