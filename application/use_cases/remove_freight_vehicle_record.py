from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError,
)
from application.ports.freight_vehicle_record_unit_of_work import (
    FreightVehicleRecordUnitOfWorkFactory,
)
from domain.models.freight import FreightStatus


class RemoveFreightVehicleRecord:

    def __init__(
        self,
        unit_of_work_factory: FreightVehicleRecordUnitOfWorkFactory,
    ):
        self._unit_of_work_factory = unit_of_work_factory

    def execute(
        self,
        freight_transport_unit_id: int,
    ) -> None:
        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError(
                "freight_transport_unit_id inválido"
            )

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
                raise FreightNotFoundError(
                    "Frete não encontrado"
                )

            if freight.current_status != FreightStatus.PENDING:
                raise InvalidFreightStateError(
                    "Somente frete pendente aceita remoção de "
                    "veículo operacional"
                )

            vehicle_record = (
                unit_of_work.vehicle_records.get_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )

            if vehicle_record is None:
                raise InvalidFreightStateError(
                    "A unidade de transporte não possui veículo "
                    "operacional registrado"
                )

            unit_of_work.vehicle_records.delete_by_transport_unit_id(
                freight_transport_unit_id
            )
            unit_of_work.commit()
