from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from domain.models.freight import FreightStatus
from domain.models.freight_event import FreightEventType
from domain.models.freight_expense import FreightExpenseType
from domain.models.freight_vehicle_record import FreightVehicleType


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
class FreightVehicleDetails:
    freight_vehicle_record_id: int
    vehicle_type: FreightVehicleType
    plate: str
    axle_count: int
    pallet_capacity_min: int
    pallet_capacity_max: int
    payload_capacity_kg: int


@dataclass(frozen=True)
class FreightDriverAssignmentDetails:
    freight_driver_assignment_id: int
    driver_id: int
    driver_name: str
    started_at: datetime
    ended_at: datetime | None
    actual_driver_amount: Decimal | None

    @property
    def is_active(self) -> bool:
        return self.ended_at is None


@dataclass(frozen=True)
class FreightTransportUnitDetails:
    freight_transport_unit_id: int
    position: int
    vehicle: FreightVehicleDetails | None
    driver_assignments: tuple[
        FreightDriverAssignmentDetails,
        ...
    ] = ()


@dataclass(frozen=True)
class FreightExpenseDetails:
    freight_expense_id: int
    expense_type: FreightExpenseType
    value: Decimal
    occurred_at: datetime
    custom_description: str | None = None
    observation: str | None = None
    is_considered: bool = True


@dataclass(frozen=True)
class FreightEventDetails:
    freight_event_id: int
    event_type: FreightEventType
    new_status: FreightStatus
    occurred_at: datetime
    previous_status: FreightStatus | None = None
    observation: str | None = None
    user_id: int | None = None


@dataclass(frozen=True)
class FreightFinancialDetails:
    freight_financial_result_id: int
    contracted_revenue: Decimal
    actual_driver_amount: Decimal
    toll_amount: Decimal
    actual_expenses_total: Decimal
    freight_insurance_total: Decimal
    tax_total: Decimal
    administrative_cost_allocated: Decimal
    total_cost: Decimal
    realized_result: Decimal
    realized_margin: Decimal | None
    finalized_at: datetime


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
    transport_units: tuple[FreightTransportUnitDetails, ...] = ()
    expenses: tuple[FreightExpenseDetails, ...] = ()
    events: tuple[FreightEventDetails, ...] = ()
    financial_result: FreightFinancialDetails | None = None
