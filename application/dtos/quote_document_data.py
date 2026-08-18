from dataclasses import dataclass
from datetime import datetime

from application.dtos.route_result import RouteResult
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)


@dataclass(frozen=True)
class CustomerDocumentData:
    name: str | None = None
    cnpj: str | None = None


@dataclass(frozen=True)
class CompanyDocumentData:
    name: str | None = None
    cnpj: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    logo: bytes | None = None


@dataclass(frozen=True)
class QuoteDocumentData:
    route_result: RouteResult
    quote_result: QuoteCalculationResult
    axle_count: int
    include_return_trip: bool

    quote_number: str | None = None
    issued_at: datetime | None = None

    customer: CustomerDocumentData | None = None
    company: CompanyDocumentData | None = None