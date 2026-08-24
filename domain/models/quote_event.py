from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from domain.models.quote import (
    QuoteStatus
)


class QuoteEventType(StrEnum):

    CREATED = "CREATED"
    CALCULATED = "CALCULATED"

    OFFERED = "OFFERED"

    NEGOTIATION_STARTED = (
        "NEGOTIATION_STARTED"
    )

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

    PRICE_CHANGED = "PRICE_CHANGED"


@dataclass(frozen=True)
class QuoteEvent:

    event_type: QuoteEventType

    quote_event_id: int | None = None
    quote_id: int | None = None
    quote_version_id: int | None = None

    previous_status: QuoteStatus | None = None
    new_status: QuoteStatus | None = None

    previous_amount: Decimal | None = None
    new_amount: Decimal | None = None

    reason_code: str | None = None
    observation: str | None = None

    user_id: int | None = None
    occurred_at: datetime | None = None