from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class FreightDriverAssignment:

    freight_transport_unit_id: int
    driver_id: int
    started_at: datetime

    freight_driver_assignment_id: int | None = None

    ended_at: datetime | None = None
    actual_driver_amount: Decimal | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        self._validate_required_id(
            self.freight_transport_unit_id,
            "freight_transport_unit_id"
        )
        self._validate_required_id(
            self.driver_id,
            "driver_id"
        )
        self._validate_optional_id(
            self.freight_driver_assignment_id,
            "freight_driver_assignment_id"
        )
        self._validate_optional_id(
            self.created_by,
            "created_by"
        )
        self._validate_optional_id(
            self.updated_by,
            "updated_by"
        )

        if self.started_at is None:
            raise ValueError(
                "started_at é obrigatório"
            )

        amount = self.actual_driver_amount

        if amount is not None:
            amount = Decimal(
                str(amount)
            )

            if amount < Decimal("0"):
                raise ValueError(
                    "actual_driver_amount não pode ser negativo"
                )

        if self.ended_at is None:
            if amount is not None:
                raise ValueError(
                    "Participação ativa não pode possuir "
                    "actual_driver_amount realizado"
                )
        else:
            if self.ended_at < self.started_at:
                raise ValueError(
                    "ended_at não pode ser anterior a started_at"
                )

            if amount is None:
                raise ValueError(
                    "Participação encerrada precisa possuir "
                    "actual_driver_amount"
                )

        object.__setattr__(
            self,
            "actual_driver_amount",
            amount
        )

    @property
    def is_active(
        self
    ) -> bool:
        return self.ended_at is None

    @staticmethod
    def _validate_required_id(
        value: int,
        field_name: str
    ) -> None:

        if value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )

    @staticmethod
    def _validate_optional_id(
        value: int | None,
        field_name: str
    ) -> None:

        if value is not None and value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )
