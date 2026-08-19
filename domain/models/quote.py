from dataclasses import dataclass
from datetime import datetime

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)


@dataclass(frozen=True)
class Quote:
    modality: str
    axle_count: int
    include_return_trip: bool
    origin: str
    destination: str
    distance: str
    calculation_result: QuoteCalculationResult
    quote_id: int | None = None
    quote_number: str | None = None
    issued_at: datetime | None = None