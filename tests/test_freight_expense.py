import unittest
from datetime import datetime, timezone
from decimal import Decimal

from domain.models.freight_expense import (
    FreightExpense,
    FreightExpenseType
)


NOW = datetime(2026, 8, 25, 16, 0, tzinfo=timezone.utc)


def make_expense(**overrides) -> FreightExpense:
    data = {
        "freight_id": 10,
        "expense_type": FreightExpenseType.MUNCK,
        "value": Decimal("850.00"),
        "occurred_at": NOW,
        "observation": "Descarga no cliente",
    }
    data.update(overrides)
    return FreightExpense(**data)


class FreightExpenseTests(unittest.TestCase):

    def test_creates_standard_expense(self) -> None:
        expense = make_expense()
        self.assertEqual(expense.expense_type, FreightExpenseType.MUNCK)
        self.assertEqual(expense.value, Decimal("850.00"))
        self.assertTrue(expense.is_considered)
        self.assertIsNone(expense.custom_description)

    def test_accepts_all_official_types(self) -> None:
        for expense_type in FreightExpenseType:
            with self.subTest(expense_type=expense_type):
                kwargs = {"expense_type": expense_type}
                if expense_type == FreightExpenseType.OUTROS:
                    kwargs["custom_description"] = "Estacionamento"
                expense = make_expense(**kwargs)
                self.assertEqual(expense.expense_type, expense_type)

    def test_accepts_persisted_not_considered_expense(self) -> None:
        expense = make_expense(is_considered=False)
        self.assertFalse(expense.is_considered)

    def test_normalizes_decimal_value(self) -> None:
        expense = make_expense(value="90.50")
        self.assertEqual(expense.value, Decimal("90.50"))

    def test_requires_positive_value(self) -> None:
        for value in ("0", "-1"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "maior que zero"):
                    make_expense(value=value)

    def test_rejects_non_finite_value(self) -> None:
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "maior que zero"):
                    make_expense(value=value)

    def test_outros_requires_custom_description(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "custom_description é obrigatório"
        ):
            make_expense(
                expense_type=FreightExpenseType.OUTROS,
                custom_description="   "
            )

    def test_other_types_reject_custom_description(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "custom_description só pode"
        ):
            make_expense(custom_description="Não permitido")

    def test_normalizes_optional_texts(self) -> None:
        expense = make_expense(
            expense_type=FreightExpenseType.OUTROS,
            custom_description="  Taxa de estacionamento  ",
            observation="  Pago no local  "
        )
        self.assertEqual(
            expense.custom_description,
            "Taxa de estacionamento"
        )
        self.assertEqual(expense.observation, "Pago no local")

    def test_blank_observation_becomes_none(self) -> None:
        expense = make_expense(observation="   ")
        self.assertIsNone(expense.observation)

    def test_rejects_missing_occurred_at(self) -> None:
        with self.assertRaisesRegex(ValueError, "occurred_at"):
            make_expense(occurred_at=None)

    def test_rejects_invalid_identifiers(self) -> None:
        with self.assertRaisesRegex(ValueError, "freight_id"):
            make_expense(freight_id=0)

        with self.assertRaisesRegex(ValueError, "freight_expense_id"):
            make_expense(freight_expense_id=0)

        with self.assertRaisesRegex(ValueError, "created_by"):
            make_expense(created_by=0)

    def test_rejects_invalid_expense_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "expense_type"):
            make_expense(expense_type="MOTORISTA")

    def test_changes_consideration_without_changing_origin_fields(self) -> None:
        expense = make_expense(
            freight_expense_id=15,
            created_at=NOW,
            created_by=3
        )

        changed = expense.with_consideration(False)

        self.assertFalse(changed.is_considered)
        self.assertTrue(expense.is_considered)
        self.assertEqual(changed.freight_expense_id, 15)
        self.assertEqual(changed.freight_id, expense.freight_id)
        self.assertEqual(changed.value, expense.value)
        self.assertEqual(changed.created_at, expense.created_at)

    def test_rejects_invalid_consideration_change(self) -> None:
        expense = make_expense()
        with self.assertRaisesRegex(ValueError, "is_considered"):
            expense.with_consideration(1)

    def test_rejects_non_boolean_is_considered(self) -> None:
        with self.assertRaisesRegex(ValueError, "is_considered"):
            make_expense(is_considered=1)


if __name__ == "__main__":
    unittest.main()
