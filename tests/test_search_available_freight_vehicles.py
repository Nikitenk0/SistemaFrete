import unittest

from application.exceptions import InvalidVehicleDataError
from application.use_cases.search_available_freight_vehicles import (
    SearchAvailableFreightVehicles,
)
from domain.models.vehicle import Vehicle, VehicleType


class FakeRepository:
    def __init__(self):
        self.calls = []
        self.result = (
            Vehicle(vehicle_id=1, plate="ABC1D23", vehicle_type=VehicleType.TRUCK),
        )

    def search_available(self, query="", limit=200):
        self.calls.append((query, limit))
        return self.result


class SearchAvailableFreightVehiclesTests(unittest.TestCase):
    def test_normalizes_query_and_delegates(self):
        repository = FakeRepository()
        result = SearchAvailableFreightVehicles(repository).execute(
            query="  ABC1D23  ", limit=50
        )
        self.assertEqual(result, repository.result)
        self.assertEqual(repository.calls, [("ABC1D23", 50)])

    def test_blank_query_is_allowed(self):
        repository = FakeRepository()
        SearchAvailableFreightVehicles(repository).execute()
        self.assertEqual(repository.calls, [("", 200)])

    def test_rejects_invalid_query_type(self):
        with self.assertRaises(InvalidVehicleDataError):
            SearchAvailableFreightVehicles(FakeRepository()).execute(query=None)

    def test_rejects_invalid_limit(self):
        with self.assertRaises(InvalidVehicleDataError):
            SearchAvailableFreightVehicles(FakeRepository()).execute(limit=201)


if __name__ == "__main__":
    unittest.main()
