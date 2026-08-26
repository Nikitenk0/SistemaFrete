import unittest
from dataclasses import replace
from datetime import date, datetime, timezone

from application.exceptions import InvalidFreightStateError
from application.use_cases.replace_pending_freight_driver import (
    ReplacePendingFreightDriver,
)
from domain.models.driver import Driver, DriverStatus
from domain.models.driver_address import DriverAddress
from domain.models.driver_bank_account import DriverBankAccount, DriverBankAccountType
from domain.models.driver_contact import DriverContact
from domain.models.freight import Freight, FreightStatus
from domain.models.freight_driver_assignment import FreightDriverAssignment
from domain.models.freight_transport_unit import FreightTransportUnit


def make_freight(status=FreightStatus.PENDING):
    now = datetime.now(timezone.utc)
    return Freight(
        freight_id=8,
        customer_id=3,
        primary_quote_id=2,
        current_status=status,
        started_at=now if status == FreightStatus.IN_PROGRESS else None,
    )


def make_unit():
    return FreightTransportUnit(
        freight_transport_unit_id=21, freight_id=8, position=1
    )


def make_assignment(driver_id=1):
    return FreightDriverAssignment(
        freight_driver_assignment_id=31,
        freight_transport_unit_id=21,
        driver_id=driver_id,
        started_at=datetime.now(timezone.utc),
    )


def make_driver(driver_id=2):
    return Driver(
        driver_id=driver_id,
        name="Motorista Teste",
        cpf="12345678901",
        rg="RG123",
        birth_date=date(1980, 1, 1),
        cnh_number="CNH123",
        cnh_category="D",
        cnh_expiration_date=date(2030, 1, 1),
        status=DriverStatus.ACTIVE,
        contacts=(DriverContact(phone="41999999999", is_primary=True),),
        addresses=(DriverAddress(
            postal_code="80000000",
            street="Rua A",
            number="10",
            district="Centro",
            city="Curitiba",
            state="PR",
            is_primary=True,
        ),),
        bank_accounts=(DriverBankAccount(
            bank_code="001",
            agency="1234",
            account="9999",
            account_type=DriverBankAccountType.CHECKING,
            is_primary=True,
        ),),
    )


class SimpleRepo:
    def __init__(self, value):
        self.value = value
    def get_by_id(self, _id):
        return self.value
    def get_by_id_for_update(self, _id):
        return self.value


class AssignmentRepo:
    def __init__(self, current, active_new=None):
        self.current = current
        self.active_new = active_new
        self.deleted_id = None
        self.added = None
    def get_active_by_transport_unit_id(self, _id):
        return self.current
    def get_active_by_driver_id(self, driver_id):
        if self.active_new is not None and self.active_new.driver_id == driver_id:
            return self.active_new
        return None
    def delete_by_id(self, assignment_id):
        self.deleted_id = assignment_id
        self.current = None
    def add(self, assignment):
        self.added = replace(assignment, freight_driver_assignment_id=44)
        self.current = self.added
        return self.added


class FakeUow:
    def __init__(self, freight, unit, current_assignment, driver, active_new=None):
        self.freights = SimpleRepo(freight)
        self.transport_units = SimpleRepo(unit)
        self.drivers = SimpleRepo(driver)
        self.driver_assignments = AssignmentRepo(current_assignment, active_new)
        self.committed = False
    def __enter__(self):
        return self
    def __exit__(self, *_args):
        return None
    def commit(self):
        self.committed = True
    def rollback(self):
        pass


class Factory:
    def __init__(self, uow):
        self.uow = uow
    def create(self):
        return self.uow


class ReplacePendingFreightDriverTests(unittest.TestCase):
    def test_replaces_planned_driver_in_pending_freight(self):
        uow = FakeUow(
            make_freight(), make_unit(), make_assignment(1), make_driver(2)
        )
        result = ReplacePendingFreightDriver(Factory(uow)).execute(21, 2)
        self.assertEqual(uow.driver_assignments.deleted_id, 31)
        self.assertEqual(result.driver_id, 2)
        self.assertTrue(uow.committed)

    def test_rejects_same_driver(self):
        uow = FakeUow(
            make_freight(), make_unit(), make_assignment(1), make_driver(1)
        )
        with self.assertRaisesRegex(InvalidFreightStateError, "motorista diferente"):
            ReplacePendingFreightDriver(Factory(uow)).execute(21, 1)

    def test_rejects_driver_with_active_assignment(self):
        active_new = make_assignment(2)
        uow = FakeUow(
            make_freight(),
            make_unit(),
            make_assignment(1),
            make_driver(2),
            active_new=active_new,
        )
        with self.assertRaisesRegex(
            InvalidFreightStateError, "participação operacional ativa"
        ):
            ReplacePendingFreightDriver(Factory(uow)).execute(21, 2)

    def test_rejects_non_pending_freight(self):
        uow = FakeUow(
            make_freight(FreightStatus.IN_PROGRESS),
            make_unit(),
            make_assignment(1),
            make_driver(2),
        )
        with self.assertRaisesRegex(InvalidFreightStateError, "Somente frete pendente"):
            ReplacePendingFreightDriver(Factory(uow)).execute(21, 2)


if __name__ == "__main__":
    unittest.main()
