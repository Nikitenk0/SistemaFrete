from dataclasses import dataclass, replace
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum


class FreightExpenseType(StrEnum):

    AJUDANTE = "AJUDANTE"
    DESCARGA = "DESCARGA"
    EMPILHADEIRA = "EMPILHADEIRA"
    MUNCK = "MUNCK"
    PALETEIRA = "PALETEIRA"
    OUTROS = "OUTROS"


@dataclass(frozen=True)
class FreightExpense:

    freight_id: int
    expense_type: FreightExpenseType
    value: Decimal
    occurred_at: datetime

    custom_description: str | None = None
    observation: str | None = None
    is_considered: bool = True

    freight_expense_id: int | None = None
    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(self) -> None:
        if self.freight_id < 1:
            raise ValueError("freight_id inválido")

        try:
            expense_type = FreightExpenseType(self.expense_type)
        except (ValueError, TypeError) as error:
            raise ValueError("expense_type inválido") from error

        try:
            value = Decimal(str(self.value))
        except (InvalidOperation, ValueError, TypeError) as error:
            raise ValueError("value inválido") from error

        if not value.is_finite() or value <= Decimal("0"):
            raise ValueError("value deve ser maior que zero")

        if self.occurred_at is None:
            raise ValueError("occurred_at é obrigatório")

        custom_description = self._normalize_optional_text(
            self.custom_description
        )
        observation = self._normalize_optional_text(
            self.observation
        )

        if expense_type == FreightExpenseType.OUTROS:
            if custom_description is None:
                raise ValueError(
                    "custom_description é obrigatório para OUTROS"
                )
        elif custom_description is not None:
            raise ValueError(
                "custom_description só pode ser informado para OUTROS"
            )

        if not isinstance(self.is_considered, bool):
            raise ValueError("is_considered inválido")

        if (
            self.freight_expense_id is not None
            and self.freight_expense_id < 1
        ):
            raise ValueError("freight_expense_id inválido")

        if self.created_by is not None and self.created_by < 1:
            raise ValueError("created_by inválido")

        object.__setattr__(self, "expense_type", expense_type)
        object.__setattr__(self, "value", value)
        object.__setattr__(
            self,
            "custom_description",
            custom_description
        )
        object.__setattr__(self, "observation", observation)


    def with_consideration(
        self,
        is_considered: bool
    ) -> "FreightExpense":
        if not isinstance(is_considered, bool):
            raise ValueError("is_considered inválido")

        return replace(
            self,
            is_considered=is_considered
        )

    @staticmethod
    def _normalize_optional_text(
        value: str | None
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None
