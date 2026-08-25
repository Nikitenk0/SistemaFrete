from dataclasses import dataclass
from datetime import date

from domain.models.driver import (
    DriverStatus
)


@dataclass(frozen=True)
class DriverListItem:

    driver_id: int
    name: str
    cpf: str
    cnh_number: str
    cnh_category: str
    cnh_expiration_date: date
    status: DriverStatus
    primary_phone: str | None = None
    primary_email: str | None = None
