from domain.models.freight_vehicle_record import (
    FreightVehicleType,
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
)


def build_freight_vehicle_selection(
    vehicle: Vehicle,
) -> tuple[FreightVehicleType, str]:
    if vehicle.vehicle_id is None:
        raise ValueError(
            "Veículo precisa estar cadastrado para ser selecionado"
        )

    if vehicle.status != VehicleStatus.ACTIVE:
        raise ValueError(
            "Somente veículo ativo pode ser selecionado"
        )

    return (
        FreightVehicleType(vehicle.vehicle_type),
        vehicle.plate,
    )
