from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FreightTransportUnit:

    freight_id: int
    position: int

    freight_transport_unit_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.freight_id < 1:
            raise ValueError(
                "freight_id inválido"
            )

        if self.position < 1:
            raise ValueError(
                "position inválido"
            )

        if (
            self.freight_transport_unit_id is not None
            and self.freight_transport_unit_id < 1
        ):
            raise ValueError(
                "freight_transport_unit_id inválido"
            )

        if (
            self.created_by is not None
            and self.created_by < 1
        ):
            raise ValueError(
                "created_by inválido"
            )
