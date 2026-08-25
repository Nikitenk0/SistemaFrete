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


def validate_freight_completion_readiness(
    transport_units: Sequence[FreightTransportUnit],
    driver_assignments: Sequence[FreightDriverAssignment],
    vehicle_records: Sequence[FreightVehicleRecord]
) -> None:

    if not transport_units:
        raise ValueError(
            "Frete precisa possuir pelo menos uma unidade "
            "de transporte para concluir"
        )

    assignments_by_unit_id: dict[
        int,
        list[FreightDriverAssignment]
    ] = {}

    for assignment in driver_assignments:
        assignments_by_unit_id.setdefault(
            assignment.freight_transport_unit_id,
            []
        ).append(
            assignment
        )

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
                "para concluir o frete"
            )

        if transport_unit_id not in vehicle_unit_ids:
            raise ValueError(
                f"Unidade de transporte {transport_unit.position} "
                "precisa possuir veículo operacional para concluir o frete"
            )

        unit_assignments = assignments_by_unit_id.get(
            transport_unit_id,
            []
        )

        if not unit_assignments:
            raise ValueError(
                f"Unidade de transporte {transport_unit.position} "
                "precisa possuir participação de motorista "
                "para concluir o frete"
            )

        if any(
            assignment.is_active
            for assignment in unit_assignments
        ):
            raise ValueError(
                f"Unidade de transporte {transport_unit.position} "
                "possui motorista ativo e não pode concluir o frete"
            )

        if any(
            assignment.ended_at is None
            or assignment.actual_driver_amount is None
            for assignment in unit_assignments
        ):
            raise ValueError(
                f"Unidade de transporte {transport_unit.position} "
                "possui participação de motorista sem encerramento "
                "completo"
            )
