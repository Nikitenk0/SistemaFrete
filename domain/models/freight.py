from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.models.freight_event import FreightEvent


class FreightStatus(StrEnum):

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Freight:

    customer_id: int
    primary_quote_id: int

    freight_id: int | None = None

    current_status: FreightStatus = (
        FreightStatus.PENDING
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None

    events: tuple[FreightEvent, ...] = ()

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.customer_id < 1:
            raise ValueError(
                "customer_id inválido"
            )

        if self.primary_quote_id < 1:
            raise ValueError(
                "primary_quote_id inválido"
            )

        if (
            self.freight_id is not None
            and self.freight_id < 1
        ):
            raise ValueError(
                "freight_id inválido"
            )

        if (
            self.created_by is not None
            and self.created_by < 1
        ):
            raise ValueError(
                "created_by inválido"
            )

        self._validate_lifecycle_dates()

    def _validate_lifecycle_dates(
        self
    ) -> None:

        if self.current_status == FreightStatus.PENDING:
            if (
                self.started_at is not None
                or self.completed_at is not None
                or self.cancelled_at is not None
            ):
                raise ValueError(
                    "Frete pendente não pode possuir "
                    "datas operacionais"
                )
            return

        if self.current_status == FreightStatus.IN_PROGRESS:
            if self.started_at is None:
                raise ValueError(
                    "Frete em andamento precisa possuir "
                    "started_at"
                )
            if (
                self.completed_at is not None
                or self.cancelled_at is not None
            ):
                raise ValueError(
                    "Frete em andamento não pode possuir "
                    "data de conclusão ou cancelamento"
                )
            return

        if self.current_status == FreightStatus.COMPLETED:
            if (
                self.started_at is None
                or self.completed_at is None
            ):
                raise ValueError(
                    "Frete concluído precisa possuir "
                    "started_at e completed_at"
                )
            if self.cancelled_at is not None:
                raise ValueError(
                    "Frete concluído não pode possuir "
                    "cancelled_at"
                )
            if self.completed_at < self.started_at:
                raise ValueError(
                    "completed_at não pode ser anterior "
                    "a started_at"
                )
            return

        if self.current_status == FreightStatus.CANCELLED:
            if self.cancelled_at is None:
                raise ValueError(
                    "Frete cancelado precisa possuir "
                    "cancelled_at"
                )
            if self.completed_at is not None:
                raise ValueError(
                    "Frete cancelado não pode possuir "
                    "completed_at"
                )
            if (
                self.started_at is not None
                and self.cancelled_at < self.started_at
            ):
                raise ValueError(
                    "cancelled_at não pode ser anterior "
                    "a started_at"
                )
