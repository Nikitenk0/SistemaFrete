from dataclasses import replace
from datetime import datetime

from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_event import (
    FreightEvent,
    FreightEventType
)


_ALLOWED_TRANSITIONS: dict[
    FreightStatus,
    frozenset[FreightStatus]
] = {
    FreightStatus.PENDING: frozenset({
        FreightStatus.IN_PROGRESS,
        FreightStatus.CANCELLED
    }),
    FreightStatus.IN_PROGRESS: frozenset({
        FreightStatus.COMPLETED,
        FreightStatus.CANCELLED
    }),
    FreightStatus.COMPLETED: frozenset(),
    FreightStatus.CANCELLED: frozenset()
}


def validate_freight_transition(
    current_status: FreightStatus,
    target_status: FreightStatus
) -> None:

    if target_status not in _ALLOWED_TRANSITIONS[
        current_status
    ]:
        raise ValueError(
            "Transição de status do frete inválida: "
            f"{current_status.value} -> "
            f"{target_status.value}"
        )


def transition_freight(
    freight: Freight,
    target_status: FreightStatus,
    occurred_at: datetime,
    user_id: int | None = None,
    observation: str | None = None
) -> Freight:

    validate_freight_transition(
        freight.current_status,
        target_status
    )

    if target_status == FreightStatus.IN_PROGRESS:
        event_type = FreightEventType.STARTED
        started_at = occurred_at
        completed_at = None
        cancelled_at = None

    elif target_status == FreightStatus.COMPLETED:
        event_type = FreightEventType.COMPLETED
        started_at = freight.started_at
        completed_at = occurred_at
        cancelled_at = None

    elif target_status == FreightStatus.CANCELLED:
        event_type = FreightEventType.CANCELLED
        started_at = freight.started_at
        completed_at = None
        cancelled_at = occurred_at

    else:
        raise ValueError(
            "Status de destino não suportado"
        )

    event = FreightEvent(
        event_type=event_type,
        previous_status=freight.current_status,
        new_status=target_status,
        freight_id=freight.freight_id,
        observation=observation,
        occurred_at=occurred_at,
        user_id=user_id
    )

    return replace(
        freight,
        current_status=target_status,
        started_at=started_at,
        completed_at=completed_at,
        cancelled_at=cancelled_at,
        events=(
            *freight.events,
            event
        )
    )
