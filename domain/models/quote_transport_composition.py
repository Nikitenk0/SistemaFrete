from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class QuoteTransportComposition:

    position: int
    axle_count: int
    include_return_trip: bool = False

    distance_km: Decimal | None = None
    driver_amount: Decimal | None = None
    toll_amount: Decimal | None = None

    quote_transport_composition_id: int | None = None
    quote_version_id: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.position < 1:
            raise ValueError(
                "Posição da composição inválida"
            )

        if self.axle_count < 1:
            raise ValueError(
                "Quantidade de eixos inválida"
            )

        non_negative_values = (
            self.distance_km,
            self.driver_amount,
            self.toll_amount
        )

        if any(
            value is not None
            and value < 0
            for value in non_negative_values
        ):
            raise ValueError(
                "Valores da composição de transporte "
                "não podem ser negativos"
            )
