from domain.models.vehicle import VehicleStatus, VehicleType


VEHICLE_STATUS_OPTIONS = {
    "Todos": None,
    "Ativos": VehicleStatus.ACTIVE,
    "Inativos": VehicleStatus.INACTIVE,
}

VEHICLE_TYPE_LABELS = {
    VehicleType.CAMINHAO_3_4: "Caminhão 3/4",
    VehicleType.TOCO: "Toco",
    VehicleType.TRUCK: "Truck",
    VehicleType.BITRUCK: "Bitruck",
    VehicleType.CARRETA: "Carreta",
    VehicleType.CARRETA_LS: "Carreta LS",
    VehicleType.CARRETA_VANDERLEIA: "Carreta Vanderleia",
}

VEHICLE_TYPE_OPTIONS = {
    "Todos": None,
    **{
        label: vehicle_type
        for vehicle_type, label in VEHICLE_TYPE_LABELS.items()
    },
}


def vehicle_status_label(status: VehicleStatus) -> str:
    normalized = VehicleStatus(status)
    return {
        VehicleStatus.ACTIVE: "Ativo",
        VehicleStatus.INACTIVE: "Inativo",
    }[normalized]


def vehicle_type_label(vehicle_type: VehicleType) -> str:
    return VEHICLE_TYPE_LABELS[VehicleType(vehicle_type)]


def format_vehicle_plate(value: str) -> str:
    plate = "".join(
        character
        for character in str(value).upper()
        if character not in {"-", " "}
    )
    if len(plate) != 7:
        return str(value)
    return f"{plate[:3]}-{plate[3:]}"
