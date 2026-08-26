from datetime import date

from domain.models.driver import DriverStatus


DRIVER_STATUS_OPTIONS = {
    "Todos": None,
    "Ativos": DriverStatus.ACTIVE,
    "Inativos": DriverStatus.INACTIVE,
}


def driver_status_label(status: DriverStatus) -> str:
    normalized = DriverStatus(status)
    return {
        DriverStatus.ACTIVE: "Ativo",
        DriverStatus.INACTIVE: "Inativo",
    }[normalized]


def format_driver_cpf(value: str) -> str:
    digits = "".join(character for character in str(value) if character.isdigit())
    if len(digits) != 11:
        return str(value)
    return (
        f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-"
        f"{digits[9:]}"
    )


def format_driver_phone(value: str | None) -> str:
    if value is None:
        return "--"

    digits = "".join(character for character in str(value) if character.isdigit())
    if len(digits) == 11:
        return (
            f"({digits[:2]}) {digits[2:7]}-"
            f"{digits[7:]}"
        )
    if len(digits) == 10:
        return (
            f"({digits[:2]}) {digits[2:6]}-"
            f"{digits[6:]}"
        )
    return str(value)


def format_driver_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")
