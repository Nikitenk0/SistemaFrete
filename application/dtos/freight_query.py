from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from domain.models.freight import FreightStatus


@dataclass(frozen=True)
class FreightQueryFilters:
    customer_id: int | None = None
    status: FreightStatus | None = None
    completed_from: datetime | None = None
    completed_to: datetime | None = None


@dataclass(frozen=True)
class FreightListItem:
    freight_id: int
    customer_id: int
    customer_name: str
    primary_quote_id: int
    primary_quote_number: str
    origin: str
    destination: str
    current_status: FreightStatus
    contracted_revenue: Decimal
    financially_closed: bool
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None


@dataclass(frozen=True)
class FreightDetails:
    freight_id: int
    customer_id: int
    customer_legal_name: str | None
    customer_trade_name: str | None
    primary_quote_id: int
    primary_quote_number: str
    origin: str
    destination: str
    current_status: FreightStatus
    contracted_revenue: Decimal
    approved_complementary_quote_count: int
    financially_closed: bool
    financial_result_id: int | None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
