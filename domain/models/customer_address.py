from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class CustomerAddressType(StrEnum):

    REGISTRATION = "REGISTRATION"
    BILLING = "BILLING"
    OTHER = "OTHER"


@dataclass(frozen=True)
class CustomerAddress:

    address_type: CustomerAddressType = (
        CustomerAddressType.REGISTRATION
    )

    postal_code: str | None = None
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None

    is_primary: bool = False

    customer_address_id: int | None = None
    customer_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None