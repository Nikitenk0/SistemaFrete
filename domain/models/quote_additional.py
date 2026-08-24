from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class QuoteAdditionalType(StrEnum):

    HELPER = "HELPER"
    MUNCK = "MUNCK"
    PALLET_JACK = "PALLET_JACK"
    FORKLIFT = "FORKLIFT"
    OTHER = "OTHER"


@dataclass(frozen=True)
class QuoteAdditional:

    additional_type: QuoteAdditionalType
    value: Decimal
    position: int

    custom_description: str | None = None

    quote_additional_id: int | None = None
    quote_version_id: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.position < 1:
            raise ValueError(
                "Posição do adicional inválida"
            )

        if self.value < 0:
            raise ValueError(
                "Valor do adicional não pode ser negativo"
            )

        description = (
            self.custom_description.strip()
            if self.custom_description
            else None
        )

        if (
            self.additional_type
            == QuoteAdditionalType.OTHER
            and not description
        ):
            raise ValueError(
                "Descrição é obrigatória "
                "para adicional do tipo OTHER"
            )

        object.__setattr__(
            self,
            "custom_description",
            description
        )