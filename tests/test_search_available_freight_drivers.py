import unittest

from application.dtos.freight_driver_selection import (
    FreightDriverSelectionItem,
)
from application.exceptions import InvalidDriverDataError
from application.use_cases.search_available_freight_drivers import (
    SearchAvailableFreightDrivers,
)


class FakeRepository:

    def __init__(self):
        self.calls = []
        self.result = (
            FreightDriverSelectionItem(
                driver_id=7,
                name="Motorista Teste",
                cpf="12345678901",
                cnh_number="99887766",
                cnh_category="E",
            ),
        )

    def search_available(
        self,
        query: str,
        limit: int = 20,
    ):
        self.calls.append((query, limit))
        return self.result


class SearchAvailableFreightDriversTests(
    unittest.TestCase
):

    def test_forwards_normalized_query_and_limit(self):
        repository = FakeRepository()

        result = SearchAvailableFreightDrivers(
            repository
        ).execute(
            query="  Joao  ",
            limit=10,
        )

        self.assertEqual(result, repository.result)
        self.assertEqual(
            repository.calls,
            [("Joao", 10)],
        )

    def test_blank_query_returns_empty_without_repository_call(self):
        repository = FakeRepository()

        result = SearchAvailableFreightDrivers(
            repository
        ).execute(
            query="   "
        )

        self.assertEqual(result, ())
        self.assertEqual(repository.calls, [])

    def test_rejects_non_string_query(self):
        repository = FakeRepository()

        with self.assertRaisesRegex(
            InvalidDriverDataError,
            "query inválida",
        ):
            SearchAvailableFreightDrivers(
                repository
            ).execute(
                query=None  # type: ignore[arg-type]
            )

    def test_rejects_invalid_limit(self):
        repository = FakeRepository()
        use_case = SearchAvailableFreightDrivers(
            repository
        )

        for invalid_limit in (0, 101):
            with self.assertRaisesRegex(
                InvalidDriverDataError,
                "limit inválido",
            ):
                use_case.execute(
                    query="Teste",
                    limit=invalid_limit,
                )


if __name__ == "__main__":
    unittest.main()
