from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class CustomerGroupStatus(StrEnum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass(frozen=True)
class CustomerGroup:

    name: str

    status: CustomerGroupStatus = (
        CustomerGroupStatus.ACTIVE
    )

    customer_group_id: int | None = None

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
                "Nome do grupo é obrigatório"
            )

        object.__setattr__(
            self,
            "name",
            name
        )