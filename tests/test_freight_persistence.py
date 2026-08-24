import unittest
from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightPersistenceError
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_event import (
    FreightEvent,
    FreightEventType
)
from infrastructure.persistence.sqlalchemy.base import (
    Base
)
import infrastructure.persistence.sqlalchemy.models  # noqa: F401
from infrastructure.persistence.sqlalchemy.freight_repository import (
    SqlAlchemyFreightRepository
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightEventModel,
    FreightModel
)


NOW = datetime(
    2026,
    8,
    24,
    18,
    0,
    tzinfo=timezone.utc
)


class FreightPersistenceMetadataTests(
    unittest.TestCase
):

    def test_registers_freight_lifecycle_columns(
        self
    ) -> None:

        table = Base.metadata.tables[
            "freights"
        ]

        self.assertIn(
            "current_status",
            table.c
        )
        self.assertIn(
            "started_at",
            table.c
        )
        self.assertIn(
            "completed_at",
            table.c
        )
        self.assertIn(
            "cancelled_at",
            table.c
        )
        self.assertFalse(
            table.c.current_status.nullable
        )

    def test_registers_freight_events_table(
        self
    ) -> None:

        table = Base.metadata.tables[
            "freight_events"
        ]

        for column_name in (
            "freight_event_id",
            "freight_id",
            "event_type",
            "previous_status",
            "new_status",
            "observation",
            "user_id",
            "occurred_at"
        ):
            self.assertIn(
                column_name,
                table.c
            )

        freight_fk = next(
            iter(
                table.c.freight_id.foreign_keys
            )
        )

        self.assertEqual(
            freight_fk.target_fullname,
            "freights.freight_id"
        )
        self.assertEqual(
            freight_fk.ondelete,
            "CASCADE"
        )


class FreightRepositoryMappingTests(
    unittest.TestCase
):

    def test_maps_domain_freight_with_event_to_model(
        self
    ) -> None:

        freight = Freight(
            customer_id=5,
            primary_quote_id=10,
            events=(
                FreightEvent(
                    event_type=(
                        FreightEventType.CREATED
                    ),
                    new_status=(
                        FreightStatus.PENDING
                    ),
                    occurred_at=NOW,
                    user_id=7
                ),
            ),
            created_at=NOW,
            created_by=7
        )

        model = (
            SqlAlchemyFreightRepository
            ._to_model(
                freight
            )
        )

        self.assertEqual(
            model.current_status,
            "PENDING"
        )
        self.assertEqual(
            len(model.events),
            1
        )
        self.assertEqual(
            model.events[0].event_type,
            "CREATED"
        )
        self.assertEqual(
            model.events[0].new_status,
            "PENDING"
        )

    def test_maps_persisted_lifecycle_to_domain(
        self
    ) -> None:

        model = FreightModel(
            freight_id=12,
            customer_id=5,
            primary_quote_id=10,
            current_status="IN_PROGRESS",
            started_at=NOW,
            created_at=NOW,
            created_by=7
        )
        model.events = [
            FreightEventModel(
                freight_event_id=21,
                freight_id=12,
                event_type="CREATED",
                previous_status=None,
                new_status="PENDING",
                occurred_at=NOW,
                user_id=7
            ),
            FreightEventModel(
                freight_event_id=22,
                freight_id=12,
                event_type="STARTED",
                previous_status="PENDING",
                new_status="IN_PROGRESS",
                occurred_at=NOW,
                user_id=7
            )
        ]

        freight = (
            SqlAlchemyFreightRepository
            ._to_domain(
                model
            )
        )

        self.assertEqual(
            freight.current_status,
            FreightStatus.IN_PROGRESS
        )
        self.assertEqual(
            freight.started_at,
            NOW
        )
        self.assertEqual(
            len(freight.events),
            2
        )
        self.assertEqual(
            freight.events[-1].event_type,
            FreightEventType.STARTED
        )

    def test_existing_events_cannot_be_removed(
        self
    ) -> None:

        model = FreightModel(
            freight_id=12,
            customer_id=5,
            primary_quote_id=10,
            current_status="PENDING",
            created_at=NOW
        )
        model.events = [
            FreightEventModel(
                freight_event_id=21,
                freight_id=12,
                event_type="CREATED",
                previous_status=None,
                new_status="PENDING",
                occurred_at=NOW
            )
        ]

        with self.assertRaises(
            FreightPersistenceError
        ):
            (
                SqlAlchemyFreightRepository
                ._sync_events(
                    model,
                    ()
                )
            )

    def test_existing_events_cannot_be_modified(
        self
    ) -> None:

        model = FreightModel(
            freight_id=12,
            customer_id=5,
            primary_quote_id=10,
            current_status="PENDING",
            created_at=NOW
        )
        model.events = [
            FreightEventModel(
                freight_event_id=21,
                freight_id=12,
                event_type="CREATED",
                previous_status=None,
                new_status="PENDING",
                observation=None,
                occurred_at=NOW
            )
        ]

        changed = FreightEvent(
            freight_event_id=21,
            freight_id=12,
            event_type=FreightEventType.CREATED,
            previous_status=None,
            new_status=FreightStatus.PENDING,
            observation="alterado",
            occurred_at=NOW
        )

        with self.assertRaises(
            FreightPersistenceError
        ):
            (
                SqlAlchemyFreightRepository
                ._sync_events(
                    model,
                    (
                        changed,
                    )
                )
            )


class FakeSession:

    def __init__(self):
        self.statement = None

    def scalar(self, statement):
        self.statement = statement
        return None


class FreightRepositoryLockingTests(
    unittest.TestCase
):

    def test_get_by_id_for_update_uses_row_lock(
        self
    ) -> None:

        session = FakeSession()
        repository = SqlAlchemyFreightRepository(
            session
        )

        result = repository.get_by_id_for_update(
            12
        )

        self.assertIsNone(
            result
        )
        self.assertIsNotNone(
            session.statement._for_update_arg
        )


if __name__ == "__main__":
    unittest.main()
