from dataclasses import dataclass
from datetime import datetime

from domain.models.vehicle import (
    VehicleType,
    normalize_vehicle_plate,
)


def _digits(value: str) -> str:
    return "".join(
        character
        for character in value
        if character.isdigit()
    )


@dataclass(frozen=True)
class FreightOperationalAssignment:
    freight_driver_assignment_id: int
    transport_provider_id: int
    vehicle_id: int

    provider_name_snapshot: str
    provider_tax_document_snapshot: str

    driver_name_snapshot: str
    driver_cpf_snapshot: str

    vehicle_plate_snapshot: str
    vehicle_type_snapshot: VehicleType

    freight_operational_assignment_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(self) -> None:
        self._required_id(
            self.freight_driver_assignment_id,
            "freight_driver_assignment_id",
        )
        self._required_id(
            self.transport_provider_id,
            "transport_provider_id",
        )
        self._required_id(
            self.vehicle_id,
            "vehicle_id",
        )
        self._optional_id(
            self.freight_operational_assignment_id,
            "freight_operational_assignment_id",
        )
        self._optional_id(
            self.created_by,
            "created_by",
        )

        provider_name = self.provider_name_snapshot.strip()
        if not provider_name:
            raise ValueError(
                "provider_name_snapshot é obrigatório"
            )

        provider_document = _digits(
            self.provider_tax_document_snapshot
        )
        if len(provider_document) not in {11, 14}:
            raise ValueError(
                "provider_tax_document_snapshot inválido"
            )

        driver_name = self.driver_name_snapshot.strip()
        if not driver_name:
            raise ValueError(
                "driver_name_snapshot é obrigatório"
            )

        driver_cpf = _digits(
            self.driver_cpf_snapshot
        )
        if len(driver_cpf) != 11:
            raise ValueError(
                "driver_cpf_snapshot inválido"
            )

        vehicle_plate = normalize_vehicle_plate(
            self.vehicle_plate_snapshot
        )

        try:
            vehicle_type = VehicleType(
                self.vehicle_type_snapshot
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "vehicle_type_snapshot inválido"
            ) from error

        object.__setattr__(
            self,
            "provider_name_snapshot",
            provider_name,
        )
        object.__setattr__(
            self,
            "provider_tax_document_snapshot",
            provider_document,
        )
        object.__setattr__(
            self,
            "driver_name_snapshot",
            driver_name,
        )
        object.__setattr__(
            self,
            "driver_cpf_snapshot",
            driver_cpf,
        )
        object.__setattr__(
            self,
            "vehicle_plate_snapshot",
            vehicle_plate,
        )
        object.__setattr__(
            self,
            "vehicle_type_snapshot",
            vehicle_type,
        )

    @staticmethod
    def _required_id(
        value: int,
        field_name: str,
    ) -> None:
        if value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )

    @staticmethod
    def _optional_id(
        value: int | None,
        field_name: str,
    ) -> None:
        if value is not None and value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )
