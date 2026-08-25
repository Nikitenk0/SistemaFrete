from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class VehicleType(StrEnum):

    CAMINHAO_3_4 = "CAMINHAO_3_4"
    TOCO = "TOCO"
    TRUCK = "TRUCK"
    BITRUCK = "BITRUCK"
    CARRETA = "CARRETA"
    CARRETA_LS = "CARRETA_LS"
    CARRETA_VANDERLEIA = "CARRETA_VANDERLEIA"


class VehicleStatus(StrEnum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


def normalize_vehicle_plate(
    value: str
) -> str:

    plate = "".join(
        character
        for character in value.upper()
        if character not in {"-", " "}
    )

    allowed_characters = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    if (
        len(plate) != 7
        or any(
            character not in allowed_characters
            for character in plate
        )
    ):
        raise ValueError(
            "plate inválida"
        )

    return plate


@dataclass(frozen=True)
class Vehicle:

    plate: str
    vehicle_type: VehicleType
    status: VehicleStatus = VehicleStatus.ACTIVE

    vehicle_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        plate = normalize_vehicle_plate(
            self.plate
        )

        try:
            vehicle_type = VehicleType(
                self.vehicle_type
            )
        except (ValueError, TypeError) as error:
            raise ValueError(
                "vehicle_type inválido"
            ) from error

        try:
            status = VehicleStatus(
                self.status
            )
        except (ValueError, TypeError) as error:
            raise ValueError(
                "status inválido"
            ) from error

        self._validate_optional_id(
            self.vehicle_id,
            "vehicle_id"
        )
        self._validate_optional_id(
            self.created_by,
            "created_by"
        )
        self._validate_optional_id(
            self.updated_by,
            "updated_by"
        )

        object.__setattr__(
            self,
            "plate",
            plate
        )
        object.__setattr__(
            self,
            "vehicle_type",
            vehicle_type
        )
        object.__setattr__(
            self,
            "status",
            status
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
