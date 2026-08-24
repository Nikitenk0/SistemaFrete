from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from domain.models.freight import (
    FreightStatus
)


class FreightEventType(StrEnum):

    CREATED = "CREATED"
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class FreightEvent:

    event_type: FreightEventType
    new_status: FreightStatus

    previous_status: FreightStatus | None = None

    freight_event_id: int | None = None
    freight_id: int | None = None

    observation: str | None = None
    occurred_at: datetime | None = None
    user_id: int | None = None

    def __post_init__(
        self
    ) -> None:

        if (
            self.freight_event_id is not None
            and self.freight_event_id < 1
        ):
            raise ValueError(
                "freight_event_id inválido"
            )

        if (
            self.freight_id is not None
            and self.freight_id < 1
        ):
            raise ValueError(
                "freight_id inválido"
            )

        if (
            self.user_id is not None
            and self.user_id < 1
        ):
            raise ValueError(
                "user_id inválido"
            )

        self._validate_status_change()

    def _validate_status_change(
        self
    ) -> None:

        expected = {
            FreightEventType.CREATED: (
                None,
                FreightStatus.PENDING
            ),
            FreightEventType.STARTED: (
                FreightStatus.PENDING,
                FreightStatus.IN_PROGRESS
            ),
            FreightEventType.COMPLETED: (
                FreightStatus.IN_PROGRESS,
                FreightStatus.COMPLETED
            )
        }

        if self.event_type in expected:
            expected_previous, expected_new = (
                expected[self.event_type]
            )
            if (
                self.previous_status != expected_previous
                or self.new_status != expected_new
            ):
                raise ValueError(
                    "Transição incompatível com o tipo "
                    "do evento de frete"
                )
            return

        if self.event_type == FreightEventType.CANCELLED:
            if (
                self.previous_status
                not in {
                    FreightStatus.PENDING,
                    FreightStatus.IN_PROGRESS
                }
                or self.new_status
                != FreightStatus.CANCELLED
            ):
                raise ValueError(
                    "Transição incompatível com evento "
                    "de cancelamento do frete"
                )
