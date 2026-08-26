from datetime import datetime
from decimal import Decimal

from domain.models.freight import FreightStatus
from domain.models.freight_event import FreightEventType
from domain.models.freight_expense import FreightExpenseType
from domain.models.freight_vehicle_record import FreightVehicleType


_STATUS_LABELS = {
    FreightStatus.PENDING: "Pendente",
    FreightStatus.IN_PROGRESS: "Em andamento",
    FreightStatus.COMPLETED: "Concluído",
    FreightStatus.CANCELLED: "Cancelado",
}

_EVENT_LABELS = {
    FreightEventType.CREATED: "Criado",
    FreightEventType.STARTED: "Iniciado",
    FreightEventType.COMPLETED: "Concluído",
    FreightEventType.CANCELLED: "Cancelado",
}

_EXPENSE_LABELS = {
    FreightExpenseType.AJUDANTE: "Ajudante",
    FreightExpenseType.DESCARGA: "Descarga",
    FreightExpenseType.EMPILHADEIRA: "Empilhadeira",
    FreightExpenseType.MUNCK: "Munck",
    FreightExpenseType.PALETEIRA: "Paleteira",
    FreightExpenseType.OUTROS: "Outros",
}

_VEHICLE_LABELS = {
    FreightVehicleType.CAMINHAO_3_4: "Caminhão 3/4",
    FreightVehicleType.TOCO: "Toco",
    FreightVehicleType.TRUCK: "Truck",
    FreightVehicleType.BITRUCK: "Bitruck",
    FreightVehicleType.CARRETA: "Carreta",
    FreightVehicleType.CARRETA_LS: "Carreta LS",
    FreightVehicleType.CARRETA_VANDERLEIA: "Carreta Vanderleia",
}


def format_currency(value: Decimal | None) -> str:
    if value is None:
        return "--"

    formatted = f"{value:,.2f}"
    formatted = (
        formatted
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )
    return f"R$ {formatted}"


def format_datetime(value: datetime | None) -> str:
    if value is None:
        return "--"

    localized = (
        value.astimezone()
        if value.tzinfo is not None
        else value
    )
    return localized.strftime("%d/%m/%Y %H:%M")


def format_margin(value: Decimal | None) -> str:
    if value is None:
        return "--"
    return f"{(value * Decimal('100')):.2f}%".replace(".", ",")


def status_label(value: FreightStatus) -> str:
    return _STATUS_LABELS[FreightStatus(value)]


def event_label(value: FreightEventType) -> str:
    return _EVENT_LABELS[FreightEventType(value)]


def expense_label(value: FreightExpenseType) -> str:
    return _EXPENSE_LABELS[FreightExpenseType(value)]


def vehicle_label(value: FreightVehicleType) -> str:
    return _VEHICLE_LABELS[FreightVehicleType(value)]


def yes_no(value: bool) -> str:
    return "Sim" if value else "Não"


def optional_text(value: str | None) -> str:
    if value is None:
        return "--"
    cleaned = value.strip()
    return cleaned if cleaned else "--"
