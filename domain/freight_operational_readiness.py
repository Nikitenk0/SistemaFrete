from collections.abc import Sequence

from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord
)


def validate_freight_operational_readiness(
    transport_units: Sequence[FreightTransportUnit],
    active_driver_assignments: Sequence[FreightDriverAssignment],
    vehicle_records: Sequence[FreightVehicleRecord]
) -> None:

    if not transport_units:
        raise ValueError(
            "Frete precisa possuir pelo menos uma unidade "
            "de transporte para iniciar"
        )

    active_driver_unit_ids = {
        assignment.freight_transport_unit_id
        for assignment in active_driver_assignments
        if assignment.is_active
    }

    vehicle_unit_ids = {
        vehicle_record.freight_transport_unit_id
        for vehicle_record in vehicle_records
    }

    ordered_units = sorted(
        transport_units,
        key=lambda transport_unit: transport_unit.position
    )

    for transport_unit in ordered_units:
        transport_unit_id = (
            transport_unit.freight_transport_unit_id
        )

        if transport_unit_id is None:
            raise ValueError(
                "Unidade de transporte precisa estar persistida "
                "para iniciar o frete"
            )

        if transport_unit_id not in active_driver_unit_ids:
            raise ValueError(
                f"Unidade de transporte {transport_unit.position} "
                "precisa possuir motorista ativo para iniciar o frete"
            )

        if transport_unit_id not in vehicle_unit_ids:
            raise ValueError(
                f"Unidade de transporte {transport_unit.position} "
                "precisa possuir veículo operacional para iniciar o frete"
            )
