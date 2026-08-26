import unittest
from datetime import datetime, timezone
from decimal import Decimal

from application.dtos.freight_query import (
    FreightDetails,
    FreightDriverAssignmentDetails,
    FreightTransportUnitDetails,
    FreightVehicleDetails,
)
from domain.models.freight import FreightStatus
from domain.models.freight_vehicle_record import (
    FreightVehicleType,
)
from presentation.desktop.freight_operational_inputs import (
    VEHICLE_TYPE_OPTIONS,
    can_start_freight,
    is_pending_setup_available,
    normalize_driver_search_query,
    parse_vehicle_record_form,
    start_readiness_message,
    unit_has_active_driver,
)


NOW = datetime(2026, 8, 25, 20, 0, tzinfo=timezone.utc)


def make_vehicle() -> FreightVehicleDetails:
    return FreightVehicleDetails(
        freight_vehicle_record_id=1,
        vehicle_type=FreightVehicleType.TRUCK,
        plate="ABC1D23",
        axle_count=3,
        pallet_capacity_min=16,
        pallet_capacity_max=20,
        payload_capacity_kg=12500,
    )


def make_active_assignment() -> FreightDriverAssignmentDetails:
    return FreightDriverAssignmentDetails(
        freight_driver_assignment_id=5,
        driver_id=9,
        driver_name="Motorista Teste",
        started_at=NOW,
        ended_at=None,
        actual_driver_amount=None,
    )


def make_unit(
    position: int = 1,
    *,
    with_vehicle: bool = True,
    with_active_driver: bool = True,
) -> FreightTransportUnitDetails:
    return FreightTransportUnitDetails(
        freight_transport_unit_id=100 + position,
        position=position,
        vehicle=(
            make_vehicle()
            if with_vehicle
            else None
        ),
        driver_assignments=(
            (make_active_assignment(),)
            if with_active_driver
            else ()
        ),
    )


def make_details(
    units=(),
    status: FreightStatus = FreightStatus.PENDING,
) -> FreightDetails:
    return FreightDetails(
        freight_id=77,
        customer_id=3,
        customer_legal_name="Empresa Teste Ltda",
        customer_trade_name="Empresa Teste",
        primary_quote_id=10,
        primary_quote_number="ORC-2026-00010",
        origin="Curitiba/PR",
        destination="Sao Paulo/SP",
        current_status=status,
        contracted_revenue=Decimal("10000"),
        approved_complementary_quote_count=0,
        financially_closed=False,
        financial_result_id=None,
        created_at=NOW,
        transport_units=tuple(units),
    )


class FreightOperationalInputsTests(unittest.TestCase):

    def test_pending_setup_is_available_only_for_pending(self):
        self.assertTrue(
            is_pending_setup_available(
                FreightStatus.PENDING
            )
        )

        for status in (
            FreightStatus.IN_PROGRESS,
            FreightStatus.COMPLETED,
            FreightStatus.CANCELLED,
        ):
            self.assertFalse(
                is_pending_setup_available(status)
            )

    def test_all_vehicle_types_are_exposed_once(self):
        self.assertEqual(
            len(VEHICLE_TYPE_OPTIONS),
            len(set(VEHICLE_TYPE_OPTIONS)),
        )
        self.assertEqual(
            len(VEHICLE_TYPE_OPTIONS),
            len(FreightVehicleType),
        )

    def test_parses_caminhao_3_4(self):
        vehicle_type, plate = parse_vehicle_record_form(
            "Caminhão 3/4",
            "ABC1D23",
        )

        self.assertEqual(
            vehicle_type,
            FreightVehicleType.CAMINHAO_3_4,
        )
        self.assertEqual(plate, "ABC1D23")

    def test_parses_carreta_ls(self):
        vehicle_type, plate = parse_vehicle_record_form(
            "Carreta LS",
            "  BRA2E19  ",
        )

        self.assertEqual(
            vehicle_type,
            FreightVehicleType.CARRETA_LS,
        )
        self.assertEqual(plate, "BRA2E19")

    def test_rejects_unknown_vehicle_label(self):
        with self.assertRaisesRegex(
            ValueError,
            "Tipo de veículo inválido",
        ):
            parse_vehicle_record_form(
                "Outro",
                "ABC1D23",
            )

    def test_rejects_empty_plate(self):
        with self.assertRaisesRegex(
            ValueError,
            "Placa é obrigatória",
        ):
            parse_vehicle_record_form(
                "Truck",
                "   ",
            )

    def test_normalizes_driver_search_query(self):
        self.assertEqual(
            normalize_driver_search_query(
                "  Maria  "
            ),
            "Maria",
        )

    def test_rejects_empty_driver_search_query(self):
        with self.assertRaisesRegex(
            ValueError,
            "Informe nome, CPF, RG ou CNH",
        ):
            normalize_driver_search_query("   ")

    def test_detects_active_driver_in_unit(self):
        self.assertTrue(
            unit_has_active_driver(
                make_unit()
            )
        )
        self.assertFalse(
            unit_has_active_driver(
                make_unit(
                    with_active_driver=False
                )
            )
        )

    def test_cannot_start_without_transport_units(self):
        details = make_details()

        self.assertFalse(
            can_start_freight(details)
        )
        self.assertIn(
            "adicione ao menos uma unidade",
            start_readiness_message(details),
        )

    def test_cannot_start_with_unit_without_vehicle(self):
        details = make_details((
            make_unit(
                with_vehicle=False
            ),
        ))

        self.assertFalse(
            can_start_freight(details)
        )
        self.assertIn(
            "registre veículo",
            start_readiness_message(details),
        )

    def test_cannot_start_with_unit_without_active_driver(self):
        details = make_details((
            make_unit(
                with_active_driver=False
            ),
        ))

        self.assertFalse(
            can_start_freight(details)
        )
        self.assertIn(
            "atribua motorista ativo",
            start_readiness_message(details),
        )

    def test_can_start_when_every_unit_has_vehicle_and_active_driver(self):
        details = make_details((
            make_unit(position=1),
            make_unit(position=2),
        ))

        self.assertTrue(
            can_start_freight(details)
        )
        self.assertEqual(
            start_readiness_message(details),
            "Frete pronto para iniciar.",
        )

    def test_non_pending_freight_cannot_start_from_setup_screen(self):
        details = make_details(
            (make_unit(),),
            status=FreightStatus.IN_PROGRESS,
        )

        self.assertFalse(
            can_start_freight(details)
        )
        self.assertEqual(
            start_readiness_message(details),
            "",
        )


if __name__ == "__main__":
    unittest.main()
