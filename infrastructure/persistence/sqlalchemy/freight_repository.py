from sqlalchemy import (
    select
)
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    selectinload
)

from application.exceptions import (
    FreightAlreadyExistsError,
    FreightPersistenceError
)
from application.ports.freight_repository import (
    FreightRepository
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_event import (
    FreightEvent,
    FreightEventType
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightEventModel,
    FreightModel
)


class SqlAlchemyFreightRepository(
    FreightRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        freight: Freight
    ) -> Freight:

        if freight.freight_id is not None:
            raise ValueError(
                "Frete já possui freight_id"
            )

        model = self._to_model(
            freight
        )

        self._session.add(
            model
        )

        try:
            self._session.flush()

        except IntegrityError as error:

            if (
                self._get_constraint_name(error)
                == "uq_freights_primary_quote_id"
            ):
                raise FreightAlreadyExistsError(
                    "O orçamento principal já possui "
                    "um frete associado"
                ) from error

            raise FreightPersistenceError(
                "Não foi possível salvar o frete"
            ) from error

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível salvar o frete"
            ) from error

        created_freight = self.get_by_id(
            model.freight_id
        )

        if created_freight is None:
            raise FreightPersistenceError(
                "Frete salvo não pôde ser recuperado"
            )

        return created_freight

    def save(
        self,
        freight: Freight
    ) -> Freight:

        if freight.freight_id is None:
            raise ValueError(
                "Frete precisa possuir freight_id"
            )

        try:
            model = self._session.scalar(
                select(
                    FreightModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    FreightModel.freight_id
                    == freight.freight_id
                )
            )

            if model is None:
                raise FreightPersistenceError(
                    "Frete não encontrado para atualização"
                )

            self._validate_identity(
                model,
                freight
            )

            self._apply_freight(
                model,
                freight
            )

            self._sync_events(
                model,
                freight.events
            )

            self._session.flush()

        except FreightPersistenceError:
            raise

        except IntegrityError as error:
            raise FreightPersistenceError(
                "Não foi possível atualizar o frete"
            ) from error

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível atualizar o frete"
            ) from error

        saved_freight = self.get_by_id(
            freight.freight_id
        )

        if saved_freight is None:
            raise FreightPersistenceError(
                "Frete atualizado não pôde ser recuperado"
            )

        return saved_freight

    def get_by_id(
        self,
        freight_id: int
    ) -> Freight | None:

        try:
            model = self._session.scalar(
                select(
                    FreightModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    FreightModel.freight_id
                    == freight_id
                )
            )

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar o frete"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def get_by_id_for_update(
        self,
        freight_id: int
    ) -> Freight | None:

        try:
            model = self._session.scalar(
                select(
                    FreightModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    FreightModel.freight_id
                    == freight_id
                )
                .with_for_update()
            )

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível bloquear o frete "
                "para atualização"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def get_by_primary_quote_id(
        self,
        primary_quote_id: int
    ) -> Freight | None:

        try:
            model = self._session.scalar(
                select(
                    FreightModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    FreightModel.primary_quote_id
                    == primary_quote_id
                )
            )

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar o frete"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    @staticmethod
    def _load_options():
        return (
            selectinload(
                FreightModel.events
            ),
        )

    @staticmethod
    def _validate_identity(
        model: FreightModel,
        freight: Freight
    ) -> None:

        if model.customer_id != freight.customer_id:
            raise FreightPersistenceError(
                "Cliente do frete não pode ser alterado"
            )

        if (
            model.primary_quote_id
            != freight.primary_quote_id
        ):
            raise FreightPersistenceError(
                "Orçamento principal do frete "
                "não pode ser alterado"
            )

    @staticmethod
    def _apply_freight(
        model: FreightModel,
        freight: Freight
    ) -> None:

        model.current_status = (
            freight.current_status.value
        )
        model.started_at = freight.started_at
        model.completed_at = freight.completed_at
        model.cancelled_at = freight.cancelled_at

    @classmethod
    def _sync_events(
        cls,
        model: FreightModel,
        events: tuple[FreightEvent, ...]
    ) -> None:

        existing_by_id = {
            event.freight_event_id: event
            for event in model.events
        }

        received_existing_ids = {
            event.freight_event_id
            for event in events
            if event.freight_event_id is not None
        }

        if set(existing_by_id) - received_existing_ids:
            raise FreightPersistenceError(
                "Eventos persistidos do frete "
                "não podem ser removidos"
            )

        for event in events:

            if event.freight_event_id is None:
                model.events.append(
                    cls._event_to_model(
                        event
                    )
                )
                continue

            event_model = existing_by_id.get(
                event.freight_event_id
            )

            if event_model is None:
                raise FreightPersistenceError(
                    "Evento não pertence ao frete persistido"
                )

            persisted_event = cls._event_to_domain(
                event_model
            )

            if persisted_event != event:
                raise FreightPersistenceError(
                    "Evento persistido do frete "
                    "não pode ser alterado"
                )

    @classmethod
    def _to_model(
        cls,
        freight: Freight
    ) -> FreightModel:

        model = FreightModel(
            customer_id=freight.customer_id,
            primary_quote_id=(
                freight.primary_quote_id
            ),
            current_status=(
                freight.current_status.value
            ),
            started_at=freight.started_at,
            completed_at=freight.completed_at,
            cancelled_at=freight.cancelled_at,
            created_by=freight.created_by
        )

        if freight.created_at is not None:
            model.created_at = freight.created_at

        model.events = [
            cls._event_to_model(
                event
            )
            for event in freight.events
        ]

        return model

    @staticmethod
    def _event_to_model(
        event: FreightEvent
    ) -> FreightEventModel:

        model = FreightEventModel(
            event_type=event.event_type.value,
            previous_status=(
                event.previous_status.value
                if event.previous_status is not None
                else None
            ),
            new_status=event.new_status.value,
            observation=event.observation,
            user_id=event.user_id
        )

        if event.freight_id is not None:
            model.freight_id = event.freight_id

        if event.occurred_at is not None:
            model.occurred_at = event.occurred_at

        return model

    @classmethod
    def _to_domain(
        cls,
        model: FreightModel
    ) -> Freight:

        return Freight(
            freight_id=model.freight_id,
            customer_id=model.customer_id,
            primary_quote_id=(
                model.primary_quote_id
            ),
            current_status=FreightStatus(
                model.current_status
            ),
            started_at=model.started_at,
            completed_at=model.completed_at,
            cancelled_at=model.cancelled_at,
            events=tuple(
                cls._event_to_domain(
                    event
                )
                for event in model.events
            ),
            created_at=model.created_at,
            created_by=model.created_by
        )

    @staticmethod
    def _event_to_domain(
        model: FreightEventModel
    ) -> FreightEvent:

        return FreightEvent(
            freight_event_id=(
                model.freight_event_id
            ),
            freight_id=model.freight_id,
            event_type=FreightEventType(
                model.event_type
            ),
            previous_status=(
                FreightStatus(
                    model.previous_status
                )
                if model.previous_status is not None
                else None
            ),
            new_status=FreightStatus(
                model.new_status
            ),
            observation=model.observation,
            occurred_at=model.occurred_at,
            user_id=model.user_id
        )

    @staticmethod
    def _get_constraint_name(
        error: IntegrityError
    ) -> str | None:

        original_error = getattr(
            error,
            "orig",
            None
        )

        diagnostics = getattr(
            original_error,
            "diag",
            None
        )

        return getattr(
            diagnostics,
            "constraint_name",
            None
        )
