from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CustomerOperationalLocation:

    name: str

    postal_code: str | None = None
    street: str | None = None
    number: str | None = None
    complement: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None

    observation: str | None = None

    is_active: bool = True

    operational_location_id: int | None = None
    customer_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        name = self.name.strip()

        if not name:
            raise ValueError(
                "Nome do local operacional é obrigatório"
            )

        object.__setattr__(
            self,
            "name",
            name
        )