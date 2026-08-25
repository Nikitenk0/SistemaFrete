from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class FreightVehicleType(StrEnum):

    CAMINHAO_3_4 = "CAMINHAO_3_4"
    TOCO = "TOCO"
    TRUCK = "TRUCK"
    BITRUCK = "BITRUCK"
    CARRETA = "CARRETA"
    CARRETA_LS = "CARRETA_LS"
    CARRETA_VANDERLEIA = "CARRETA_VANDERLEIA"


@dataclass(frozen=True)
class FreightVehicleSpecification:

    axle_count: int
    pallet_capacity_min: int
    pallet_capacity_max: int
    payload_capacity_kg: int


FREIGHT_VEHICLE_SPECIFICATIONS = {
    FreightVehicleType.CAMINHAO_3_4: FreightVehicleSpecification(
        axle_count=2,
        pallet_capacity_min=8,
        pallet_capacity_max=8,
        payload_capacity_kg=3500
    ),
    FreightVehicleType.TOCO: FreightVehicleSpecification(
        axle_count=2,
        pallet_capacity_min=12,
        pallet_capacity_max=12,
        payload_capacity_kg=6500
    ),
    FreightVehicleType.TRUCK: FreightVehicleSpecification(
        axle_count=3,
        pallet_capacity_min=16,
        pallet_capacity_max=20,
        payload_capacity_kg=12500
    ),
    FreightVehicleType.BITRUCK: FreightVehicleSpecification(
        axle_count=4,
        pallet_capacity_min=16,
        pallet_capacity_max=18,
        payload_capacity_kg=17000
    ),
    FreightVehicleType.CARRETA: FreightVehicleSpecification(
        axle_count=5,
        pallet_capacity_min=28,
        pallet_capacity_max=28,
        payload_capacity_kg=26000
    ),
    FreightVehicleType.CARRETA_LS: FreightVehicleSpecification(
        axle_count=6,
        pallet_capacity_min=28,
        pallet_capacity_max=28,
        payload_capacity_kg=30000
    ),
    FreightVehicleType.CARRETA_VANDERLEIA: FreightVehicleSpecification(
        axle_count=6,
        pallet_capacity_min=30,
        pallet_capacity_max=30,
        payload_capacity_kg=35000
    )
}


def get_freight_vehicle_specification(
    vehicle_type: FreightVehicleType
) -> FreightVehicleSpecification:

    try:
        normalized_type = FreightVehicleType(
            vehicle_type
        )
    except (ValueError, TypeError) as error:
        raise ValueError(
            "vehicle_type inválido"
        ) from error

    return FREIGHT_VEHICLE_SPECIFICATIONS[
        normalized_type
    ]


@dataclass(frozen=True)
class FreightVehicleRecord:

    freight_transport_unit_id: int
    vehicle_type: FreightVehicleType
    plate: str

    axle_count: int
    pallet_capacity_min: int
    pallet_capacity_max: int
    payload_capacity_kg: int

    freight_vehicle_record_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.freight_transport_unit_id < 1:
            raise ValueError(
                "freight_transport_unit_id inválido"
            )

        try:
            vehicle_type = FreightVehicleType(
                self.vehicle_type
            )
        except (ValueError, TypeError) as error:
            raise ValueError(
                "vehicle_type inválido"
            ) from error

        plate = "".join(
            character
            for character in self.plate.upper()
            if character not in {"-", " "}
        )

        allowed_plate_characters = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        )

        if (
            len(plate) != 7
            or any(
                character not in allowed_plate_characters
                for character in plate
            )
        ):
            raise ValueError(
                "plate inválida"
            )

        if self.axle_count < 1:
            raise ValueError(
                "axle_count inválido"
            )

        if self.pallet_capacity_min < 1:
            raise ValueError(
                "pallet_capacity_min inválido"
            )

        if (
            self.pallet_capacity_max
            < self.pallet_capacity_min
        ):
            raise ValueError(
                "pallet_capacity_max inválido"
            )

        if self.payload_capacity_kg < 1:
            raise ValueError(
                "payload_capacity_kg inválido"
            )

        if (
            self.freight_vehicle_record_id is not None
            and self.freight_vehicle_record_id < 1
        ):
            raise ValueError(
                "freight_vehicle_record_id inválido"
            )

        if (
            self.created_by is not None
            and self.created_by < 1
        ):
            raise ValueError(
                "created_by inválido"
            )

        object.__setattr__(
            self,
            "vehicle_type",
            vehicle_type
        )
        object.__setattr__(
            self,
            "plate",
            plate
        )
