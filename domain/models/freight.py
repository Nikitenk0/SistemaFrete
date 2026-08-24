from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Freight:

    customer_id: int
    primary_quote_id: int

    freight_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.customer_id < 1:
            raise ValueError(
                "customer_id inválido"
            )

        if self.primary_quote_id < 1:
            raise ValueError(
                "primary_quote_id inválido"
            )

        if (
            self.freight_id is not None
            and self.freight_id < 1
        ):
            raise ValueError(
                "freight_id inválido"
            )

        if (
            self.created_by is not None
            and self.created_by < 1
        ):
            raise ValueError(
                "created_by inválido"
            )
