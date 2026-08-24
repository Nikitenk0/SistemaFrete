import unittest

from domain.models.freight import (
    Freight
)
from infrastructure.persistence.sqlalchemy.base import (
    Base
)
import infrastructure.persistence.sqlalchemy.models  # noqa: F401


class FreightDomainTests(unittest.TestCase):

    def test_creates_freight_identity(
        self
    ) -> None:

        freight = Freight(
            customer_id=10,
            primary_quote_id=20
        )

        self.assertEqual(
            freight.customer_id,
            10
        )
        self.assertEqual(
            freight.primary_quote_id,
            20
        )
        self.assertIsNone(
            freight.freight_id
        )

    def test_rejects_invalid_identity(
        self
    ) -> None:

        with self.assertRaises(ValueError):
            Freight(
                customer_id=0,
                primary_quote_id=20
            )

        with self.assertRaises(ValueError):
            Freight(
                customer_id=10,
                primary_quote_id=0
            )


class FreightPersistenceMetadataTests(unittest.TestCase):

    def test_registers_freights_table_with_expected_links(
        self
    ) -> None:

        freight_table = Base.metadata.tables[
            "freights"
        ]

        self.assertIn(
            "freight_id",
            freight_table.c
        )
        self.assertIn(
            "customer_id",
            freight_table.c
        )
        self.assertIn(
            "primary_quote_id",
            freight_table.c
        )

        customer_fk = next(
            iter(
                freight_table.c.customer_id.foreign_keys
            )
        )
        primary_quote_fk = next(
            iter(
                freight_table.c.primary_quote_id.foreign_keys
            )
        )

        self.assertEqual(
            customer_fk.target_fullname,
            "customers.customer_id"
        )
        self.assertEqual(
            customer_fk.ondelete,
            "RESTRICT"
        )
        self.assertEqual(
            primary_quote_fk.target_fullname,
            "quotes.quote_id"
        )
        self.assertEqual(
            primary_quote_fk.ondelete,
            "RESTRICT"
        )

        unique_columns = {
            tuple(
                column.name
                for column in constraint.columns
            )
            for constraint in freight_table.constraints
            if constraint.__class__.__name__
            == "UniqueConstraint"
        }

        self.assertIn(
            ("primary_quote_id",),
            unique_columns
        )

    def test_links_quote_to_freight_with_set_null(
        self
    ) -> None:

        quote_table = Base.metadata.tables[
            "quotes"
        ]

        freight_fk = next(
            iter(
                quote_table.c.freight_id.foreign_keys
            )
        )

        self.assertEqual(
            freight_fk.target_fullname,
            "freights.freight_id"
        )
        self.assertEqual(
            freight_fk.ondelete,
            "SET NULL"
        )


if __name__ == "__main__":
    unittest.main()
