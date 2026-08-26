from application.dtos.freight_query import (
    FreightDetails,
    FreightTransportUnitDetails,
)
from domain.models.freight import FreightStatus
from domain.models.freight_vehicle_record import (
    FreightVehicleType,
)


VEHICLE_TYPE_OPTIONS = (
    "Caminhão 3/4",
    "Toco",
    "Truck",
    "Bitruck",
    "Carreta",
    "Carreta LS",
    "Carreta Vanderleia",
)


_VEHICLE_TYPE_BY_LABEL = {
    "Caminhão 3/4": FreightVehicleType.CAMINHAO_3_4,
    "Toco": FreightVehicleType.TOCO,
    "Truck": FreightVehicleType.TRUCK,
    "Bitruck": FreightVehicleType.BITRUCK,
    "Carreta": FreightVehicleType.CARRETA,
    "Carreta LS": FreightVehicleType.CARRETA_LS,
    "Carreta Vanderleia": FreightVehicleType.CARRETA_VANDERLEIA,
}


def is_pending_setup_available(
    status: FreightStatus,
) -> bool:
    return status == FreightStatus.PENDING


def parse_vehicle_record_form(
    vehicle_type_label: str,
    plate_text: str,
) -> tuple[FreightVehicleType, str]:
    try:
        vehicle_type = _VEHICLE_TYPE_BY_LABEL[
            vehicle_type_label
        ]
    except KeyError as error:
        raise ValueError(
            "Tipo de veículo inválido"
        ) from error

    plate = plate_text.strip()
    if not plate:
        raise ValueError(
            "Placa é obrigatória"
        )

    return vehicle_type, plate


def normalize_driver_search_query(
    query_text: str,
) -> str:
    query = query_text.strip()

    if not query:
        raise ValueError(
            "Informe nome, CPF, RG ou CNH do motorista"
        )

    return query


def unit_has_active_driver(
    unit: FreightTransportUnitDetails,
) -> bool:
    return any(
        assignment.is_active
        for assignment in unit.driver_assignments
    )


def can_start_freight(
    details: FreightDetails,
) -> bool:
    if details.current_status != FreightStatus.PENDING:
        return False

    if not details.transport_units:
        return False

    return all(
        unit.vehicle is not None
        and unit_has_active_driver(unit)
        for unit in details.transport_units
    )


def start_readiness_message(
    details: FreightDetails,
) -> str:
    if details.current_status != FreightStatus.PENDING:
        return ""

    if not details.transport_units:
        return (
            "Para iniciar: adicione ao menos uma unidade "
            "de transporte."
        )

    missing_vehicle_positions = [
        str(unit.position)
        for unit in details.transport_units
        if unit.vehicle is None
    ]
    if missing_vehicle_positions:
        return (
            "Para iniciar: registre veículo na(s) unidade(s) "
            + ", ".join(missing_vehicle_positions)
            + "."
        )

    missing_driver_positions = [
        str(unit.position)
        for unit in details.transport_units
        if not unit_has_active_driver(unit)
    ]
    if missing_driver_positions:
        return (
            "Para iniciar: atribua motorista ativo na(s) unidade(s) "
            + ", ".join(missing_driver_positions)
            + "."
        )

    return "Frete pronto para iniciar."
