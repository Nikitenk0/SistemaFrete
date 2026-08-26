import unittest

from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import SQLAlchemyError

from application.exceptions import DriverPersistenceError
from infrastructure.persistence.sqlalchemy.freight_driver_selection_repository import (
    SqlAlchemyFreightDriverSelectionRepository,
)


class FakeResult:

    def __init__(self, rows):
        self._rows = list(rows)

    def mappings(self):
        return self

    def all(self):
        return list(self._rows)


class FakeSession:

    def __init__(self, rows=(), error=None):
        self.rows = rows
        self.error = error
        self.statements = []

    def execute(self, statement):
        self.statements.append(statement)
        if self.error is not None:
            raise self.error
        return FakeResult(self.rows)


def compile_sql(statement) -> str:
    return str(
        statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


class FreightDriverSelectionRepositoryTests(
    unittest.TestCase
):

    def test_maps_lightweight_driver_projection(self):
        session = FakeSession(rows=(
            {
                "driver_id": 9,
                "name": "Joao da Silva",
                "cpf": "12345678901",
                "cnh_number": "44556677",
                "cnh_category": "E",
            },
        ))
        repository = (
            SqlAlchemyFreightDriverSelectionRepository(
                session
            )
        )

        result = repository.search_available(
            "Joao"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].driver_id, 9)
        self.assertEqual(result[0].name, "Joao da Silva")
        self.assertEqual(result[0].cpf, "12345678901")

        sql = compile_sql(session.statements[0])
        self.assertIn("drivers.driver_id", sql)
        self.assertNotIn("driver_contacts", sql)
        self.assertNotIn("driver_addresses", sql)
        self.assertNotIn("driver_bank_accounts", sql)

    def test_filters_active_and_without_active_assignment(self):
        session = FakeSession()
        repository = (
            SqlAlchemyFreightDriverSelectionRepository(
                session
            )
        )

        repository.search_available(
            "Maria",
            limit=12,
        )

        sql = compile_sql(session.statements[0])
        self.assertIn("drivers.status = 'ACTIVE'", sql)
        self.assertIn("NOT (EXISTS", sql)
        self.assertIn("freight_driver_assignments.driver_id = drivers.driver_id", sql)
        self.assertIn("freight_driver_assignments.ended_at IS NULL", sql)
        self.assertIn("LIMIT 12", sql)

    def test_searches_name_rg_cnh_and_numeric_cpf(self):
        session = FakeSession()
        repository = (
            SqlAlchemyFreightDriverSelectionRepository(
                session
            )
        )

        repository.search_available(
            "123.456"
        )

        sql = compile_sql(session.statements[0])
        self.assertIn("drivers.name ILIKE", sql)
        self.assertIn("drivers.rg ILIKE", sql)
        self.assertIn("drivers.cnh_number ILIKE", sql)
        self.assertIn("drivers.cpf LIKE", sql)
        self.assertIn("123456", sql)

    def test_wraps_sqlalchemy_error(self):
        repository = (
            SqlAlchemyFreightDriverSelectionRepository(
                FakeSession(
                    error=SQLAlchemyError("boom")
                )
            )
        )

        with self.assertRaisesRegex(
            DriverPersistenceError,
            "motoristas disponíveis",
        ):
            repository.search_available(
                "Teste"
            )


if __name__ == "__main__":
    unittest.main()
