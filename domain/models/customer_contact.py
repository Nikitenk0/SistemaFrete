from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CustomerContact:

    name: str | None = None

    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None

    position_or_department: str | None = None

    is_primary: bool = False

    customer_contact_id: int | None = None
    customer_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None