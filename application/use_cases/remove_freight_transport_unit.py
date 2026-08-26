from application.exceptions import (
    FreightNotFoundError,
    FreightTransportUnitNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.ports.freight_unit_of_work import (
    FreightUnitOfWorkFactory
)
from domain.models.freight import (
    FreightStatus
)


class RemoveFreightTransportUnit:

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
        freight_transport_unit_id: int
    ) -> None:

        if freight_transport_unit_id < 1:
            raise InvalidFreightDataError(
                "freight_transport_unit_id inválido"
            )

        with (
            self._freight_unit_of_work_factory.create()
            as unit_of_work
        ):
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

            if freight.current_status != FreightStatus.PENDING:
                raise InvalidFreightStateError(
                    "Somente frete pendente aceita remoção "
                    "de unidade de transporte"
                )

            units = (
                unit_of_work.transport_units
                .list_by_freight_id(
                    transport_unit.freight_id
                )
            )

            last_unit = max(
                units,
                key=lambda unit: unit.position,
                default=None
            )

            if (
                last_unit is None
                or last_unit.freight_transport_unit_id
                != freight_transport_unit_id
            ):
                raise InvalidFreightStateError(
                    "Somente a última unidade de transporte "
                    "pode ser removida"
                )

            vehicle = (
                unit_of_work.vehicle_records
                .get_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )

            if vehicle is not None:
                raise InvalidFreightStateError(
                    "Unidade com veículo operacional não pode "
                    "ser removida"
                )

            assignments = (
                unit_of_work.driver_assignments
                .list_by_transport_unit_id(
                    freight_transport_unit_id
                )
            )

            if assignments:
                raise InvalidFreightStateError(
                    "Unidade com participação de motorista não "
                    "pode ser removida"
                )

            unit_of_work.transport_units.delete_by_id(
                freight_transport_unit_id
            )
            unit_of_work.commit()
