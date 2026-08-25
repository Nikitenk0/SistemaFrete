import unittest
from datetime import (
    datetime,
    time,
    timezone,
)

from domain.models.freight import FreightStatus
from presentation.desktop.freight_list_filters import (
    freight_status_label,
    parse_freight_list_filters,
)


class FreightListFiltersTest(unittest.TestCase):

    def test_empty_filters(self):
        filters = parse_freight_list_filters(
            customer_id_text="",
            status_label="Todos",
            completed_from_text="",
            completed_to_text="",
            timezone_info=timezone.utc,
        )

        self.assertIsNone(filters.customer_id)
        self.assertIsNone(filters.status)
        self.assertIsNone(filters.completed_from)
        self.assertIsNone(filters.completed_to)

    def test_customer_and_status(self):
        filters = parse_freight_list_filters(
            customer_id_text=" 15 ",
            status_label="Em andamento",
            completed_from_text="",
            completed_to_text="",
            timezone_info=timezone.utc,
        )

        self.assertEqual(filters.customer_id, 15)
        self.assertEqual(
            filters.status,
            FreightStatus.IN_PROGRESS,
        )

    def test_invalid_customer_text(self):
        with self.assertRaisesRegex(
            ValueError,
            "número inteiro",
        ):
            parse_freight_list_filters(
                customer_id_text="ABC",
                status_label="Todos",
                completed_from_text="",
                completed_to_text="",
                timezone_info=timezone.utc,
            )

    def test_invalid_customer_zero(self):
        with self.assertRaisesRegex(
            ValueError,
            "maior que zero",
        ):
            parse_freight_list_filters(
                customer_id_text="0",
                status_label="Todos",
                completed_from_text="",
                completed_to_text="",
                timezone_info=timezone.utc,
            )

    def test_completion_dates_are_inclusive_days(self):
        filters = parse_freight_list_filters(
            customer_id_text="",
            status_label="Concluído",
            completed_from_text="01/08/2026",
            completed_to_text="31/08/2026",
            timezone_info=timezone.utc,
        )

        self.assertEqual(
            filters.completed_from,
            datetime.combine(
                datetime(2026, 8, 1).date(),
                time.min,
            ).replace(tzinfo=timezone.utc),
        )
        self.assertEqual(
            filters.completed_to,
            datetime.combine(
                datetime(2026, 8, 31).date(),
                time.max,
            ).replace(tzinfo=timezone.utc),
        )

    def test_invalid_date_format(self):
        with self.assertRaisesRegex(
            ValueError,
            "DD/MM/AAAA",
        ):
            parse_freight_list_filters(
                customer_id_text="",
                status_label="Todos",
                completed_from_text="2026-08-01",
                completed_to_text="",
                timezone_info=timezone.utc,
            )

    def test_completion_period_rejects_non_completed_status(self):
        with self.assertRaisesRegex(
            ValueError,
            "status Concluído ou Todos",
        ):
            parse_freight_list_filters(
                customer_id_text="",
                status_label="Pendente",
                completed_from_text="01/08/2026",
                completed_to_text="31/08/2026",
                timezone_info=timezone.utc,
            )

    def test_inverted_period(self):
        with self.assertRaisesRegex(
            ValueError,
            "Data final",
        ):
            parse_freight_list_filters(
                customer_id_text="",
                status_label="Concluído",
                completed_from_text="31/08/2026",
                completed_to_text="01/08/2026",
                timezone_info=timezone.utc,
            )

    def test_status_labels(self):
        self.assertEqual(
            freight_status_label(
                FreightStatus.PENDING
            ),
            "Pendente",
        )
        self.assertEqual(
            freight_status_label(
                FreightStatus.IN_PROGRESS
            ),
            "Em andamento",
        )
        self.assertEqual(
            freight_status_label(
                FreightStatus.COMPLETED
            ),
            "Concluído",
        )
        self.assertEqual(
            freight_status_label(
                FreightStatus.CANCELLED
            ),
            "Cancelado",
        )


if __name__ == "__main__":
    unittest.main()
