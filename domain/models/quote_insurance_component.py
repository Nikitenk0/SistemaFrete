from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class QuoteInsuranceType(StrEnum):

    RCTRC = "RCTRC"
    RCDC = "RCDC"
    LIFE = "LIFE"
    ACCIDENT = "ACCIDENT"


@dataclass(frozen=True)
class QuoteInsuranceComponent:

    insurance_type: QuoteInsuranceType
    value: Decimal
    position: int

    calculation_base: Decimal | None = None
    rate: Decimal | None = None

    quote_insurance_component_id: int | None = None
    quote_version_id: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.position < 1:
            raise ValueError(
                "Posição do seguro inválida"
            )

        if self.value < 0:
            raise ValueError(
                "Valor do seguro não pode ser negativo"
            )

        if (
            self.calculation_base is not None
            and self.calculation_base < 0
        ):
            raise ValueError(
                "Base de cálculo do seguro "
                "não pode ser negativa"
            )

        if (
            self.rate is not None
            and self.rate < 0
        ):
            raise ValueError(
                "Alíquota do seguro "
                "não pode ser negativa"
            )