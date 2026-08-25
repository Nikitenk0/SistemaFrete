import unittest
from datetime import (
    datetime,
    timedelta,
    timezone
)
from decimal import Decimal

from domain.freight_completion_readiness import (
    validate_freight_completion_readiness
)
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType,
    get_freight_vehicle_specification
)


NOW = datetime(
    2026,
    8,
    25,
    15,
    0,
    tzinfo=timezone.utc
)


def make_transport_unit(
    unit_id: int,
    position: int
) -> FreightTransportUnit:
    return FreightTransportUnit(
        freight_transport_unit_id=unit_id,
        freight_id=77,
        position=position,
        created_at=NOW
    )


def make_active_assignment(
    unit_id: int,
    driver_id: int
) -> FreightDriverAssignment:
    return FreightDriverAssignment(
        freight_driver_assignment_id=(
            1000 + unit_id + driver_id
        ),
        freight_transport_unit_id=unit_id,
        driver_id=driver_id,
        started_at=NOW,
        created_at=NOW,
        updated_at=NOW
    )


def make_finished_assignment(
    unit_id: int,
    driver_id: int,
    amount: str = "1000.00",
    minute_offset: int = 0
) -> FreightDriverAssignment:
    started_at = NOW + timedelta(
        minutes=minute_offset
    )
    ended_at = started_at + timedelta(
        hours=1
    )

    return FreightDriverAssignment(
        freight_driver_assignment_id=(
            2000 + unit_id + driver_id + minute_offset
        ),
        freight_transport_unit_id=unit_id,
        driver_id=driver_id,
        started_at=started_at,
        ended_at=ended_at,
        actual_driver_amount=Decimal(amount),
        created_at=started_at,
        updated_at=ended_at
    )


def make_vehicle_record(
    unit_id: int,
    plate: str
) -> FreightVehicleRecord:
    vehicle_type = FreightVehicleType.TRUCK
    specification = get_freight_vehicle_specification(
        vehicle_type
    )

    return FreightVehicleRecord(
        freight_vehicle_record_id=(
            3000 + unit_id
        ),
        freight_transport_unit_id=unit_id,
        vehicle_type=vehicle_type,
        plate=plate,
        axle_count=specification.axle_count,
        pallet_capacity_min=(
            specification.pallet_capacity_min
        ),
        pallet_capacity_max=(
            specification.pallet_capacity_max
        ),
        payload_capacity_kg=(
            specification.payload_capacity_kg
        ),
        created_at=NOW
    )


class FreightCompletionReadinessTests(
    unittest.TestCase
):

    def test_rejects_freight_without_transport_units(
        self
    ) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "pelo menos uma unidade de transporte"
        ):
            validate_freight_completion_readiness(
                transport_units=(),
                driver_assignments=(),
                vehicle_records=()
            )

    def test_rejects_non_persisted_transport_unit(
        self
    ) -> None:
        unit = FreightTransportUnit(
            freight_id=77,
            position=1,
            created_at=NOW
        )

        with self.assertRaisesRegex(
            ValueError,
            "precisa estar persistida"
        ):
            validate_freight_completion_readiness(
                transport_units=(unit,),
                driver_assignments=(),
                vehicle_records=()
            )

    def test_rejects_unit_without_vehicle(
        self
    ) -> None:
        unit = make_transport_unit(
            101,
            1
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unidade de transporte 1.*veículo operacional"
        ):
            validate_freight_completion_readiness(
                transport_units=(unit,),
                driver_assignments=(
                    make_finished_assignment(
                        101,
                        8
                    ),
                ),
                vehicle_records=()
            )

    def test_rejects_unit_without_driver_assignment(
        self
    ) -> None:
        unit = make_transport_unit(
            101,
            1
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unidade de transporte 1.*participação de motorista"
        ):
            validate_freight_completion_readiness(
                transport_units=(unit,),
                driver_assignments=(),
                vehicle_records=(
                    make_vehicle_record(
                        101,
                        "ABC1D23"
                    ),
                )
            )

    def test_rejects_unit_with_active_driver(
        self
    ) -> None:
        unit = make_transport_unit(
            101,
            1
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unidade de transporte 1.*motorista ativo"
        ):
            validate_freight_completion_readiness(
                transport_units=(unit,),
                driver_assignments=(
                    make_finished_assignment(
                        101,
                        8
                    ),
                    make_active_assignment(
                        101,
                        9
                    )
                ),
                vehicle_records=(
                    make_vehicle_record(
                        101,
                        "ABC1D23"
                    ),
                )
            )

    def test_rejects_first_incomplete_unit_by_position(
        self
    ) -> None:
        unit_1 = make_transport_unit(
            101,
            1
        )
        unit_2 = make_transport_unit(
            102,
            2
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unidade de transporte 2.*participação de motorista"
        ):
            validate_freight_completion_readiness(
                transport_units=(
                    unit_2,
                    unit_1
                ),
                driver_assignments=(
                    make_finished_assignment(
                        101,
                        8
                    ),
                ),
                vehicle_records=(
                    make_vehicle_record(
                        101,
                        "ABC1D23"
                    ),
                    make_vehicle_record(
                        102,
                        "DEF4G56"
                    )
                )
            )

    def test_accepts_one_completed_transport_unit(
        self
    ) -> None:
        validate_freight_completion_readiness(
            transport_units=(
                make_transport_unit(
                    101,
                    1
                ),
            ),
            driver_assignments=(
                make_finished_assignment(
                    101,
                    8,
                    "2000.00"
                ),
            ),
            vehicle_records=(
                make_vehicle_record(
                    101,
                    "ABC1D23"
                ),
            )
        )

    def test_accepts_multiple_units_and_historical_assignments(
        self
    ) -> None:
        validate_freight_completion_readiness(
            transport_units=(
                make_transport_unit(
                    101,
                    1
                ),
                make_transport_unit(
                    102,
                    2
                )
            ),
            driver_assignments=(
                make_finished_assignment(
                    101,
                    8,
                    "2000.00"
                ),
                make_finished_assignment(
                    101,
                    10,
                    "2300.00",
                    minute_offset=70
                ),
                make_finished_assignment(
                    102,
                    9,
                    "3800.00"
                )
            ),
            vehicle_records=(
                make_vehicle_record(
                    101,
                    "ABC1D23"
                ),
                make_vehicle_record(
                    102,
                    "DEF4G56"
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
