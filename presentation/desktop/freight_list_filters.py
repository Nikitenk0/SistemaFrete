from dataclasses import dataclass
from datetime import (
    datetime,
    time,
    tzinfo,
)

from domain.models.freight import FreightStatus


STATUS_LABEL_TO_VALUE = {
    "Todos": None,
    "Pendente": FreightStatus.PENDING,
    "Em andamento": FreightStatus.IN_PROGRESS,
    "Concluído": FreightStatus.COMPLETED,
    "Cancelado": FreightStatus.CANCELLED,
}

STATUS_OPTIONS = tuple(
    STATUS_LABEL_TO_VALUE.keys()
)

STATUS_VALUE_TO_LABEL = {
    status: label
    for label, status in STATUS_LABEL_TO_VALUE.items()
    if status is not None
}


@dataclass(frozen=True)
class FreightListFilterValues:
    customer_id: int | None
    status: FreightStatus | None
    completed_from: datetime | None
    completed_to: datetime | None


def parse_freight_list_filters(
    *,
    customer_id_text: str,
    status_label: str,
    completed_from_text: str,
    completed_to_text: str,
    timezone_info: tzinfo | None,
) -> FreightListFilterValues:

    customer_id = _parse_customer_id(
        customer_id_text
    )

    try:
        status = STATUS_LABEL_TO_VALUE[
            status_label
        ]
    except KeyError as error:
        raise ValueError(
            "Status de frete inválido"
        ) from error

    completed_from = _parse_date(
        completed_from_text,
        end_of_day=False,
        timezone_info=timezone_info,
    )

    completed_to = _parse_date(
        completed_to_text,
        end_of_day=True,
        timezone_info=timezone_info,
    )

    has_completion_period = (
        completed_from is not None
        or completed_to is not None
    )

    if (
        has_completion_period
        and status is not None
        and status != FreightStatus.COMPLETED
    ):
        raise ValueError(
            "Período de conclusão exige status "
            "Concluído ou Todos"
        )

    if (
        completed_from is not None
        and completed_to is not None
        and completed_to < completed_from
    ):
        raise ValueError(
            "Data final não pode ser anterior à data inicial"
        )

    return FreightListFilterValues(
        customer_id=customer_id,
        status=status,
        completed_from=completed_from,
        completed_to=completed_to,
    )


def freight_status_label(
    status: FreightStatus,
) -> str:
    try:
        return STATUS_VALUE_TO_LABEL[
            status
        ]
    except KeyError as error:
        raise ValueError(
            "Status de frete inválido"
        ) from error


def _parse_customer_id(
    value: str,
) -> int | None:

    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    try:
        customer_id = int(
            cleaned_value
        )
    except ValueError as error:
        raise ValueError(
            "Cliente ID precisa ser um número inteiro"
        ) from error

    if customer_id < 1:
        raise ValueError(
            "Cliente ID precisa ser maior que zero"
        )

    return customer_id


def _parse_date(
    value: str,
    *,
    end_of_day: bool,
    timezone_info: tzinfo | None,
) -> datetime | None:

    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    try:
        parsed_date = datetime.strptime(
            cleaned_value,
            "%d/%m/%Y",
        ).date()
    except ValueError as error:
        raise ValueError(
            "Data inválida. Use o formato DD/MM/AAAA"
        ) from error

    parsed_datetime = datetime.combine(
        parsed_date,
        time.max if end_of_day else time.min,
    )

    if timezone_info is not None:
        parsed_datetime = parsed_datetime.replace(
            tzinfo=timezone_info
        )

    return parsed_datetime
