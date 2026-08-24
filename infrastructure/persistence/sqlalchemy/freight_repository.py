from sqlalchemy import (
    select
)
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session
)

from application.exceptions import (
    FreightAlreadyExistsError,
    FreightPersistenceError
)
from application.ports.freight_repository import (
    FreightRepository
)
from domain.models.freight import (
    Freight
)
from infrastructure.persistence.sqlalchemy.models import (
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

        model = FreightModel(
            customer_id=freight.customer_id,
            primary_quote_id=(
                freight.primary_quote_id
            ),
            created_by=freight.created_by
        )

        if freight.created_at is not None:
            model.created_at = (
                freight.created_at
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

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        freight_id: int
    ) -> Freight | None:

        try:
            model = self._session.scalar(
                select(
                    FreightModel
                ).where(
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

    def get_by_primary_quote_id(
        self,
        primary_quote_id: int
    ) -> Freight | None:

        try:
            model = self._session.scalar(
                select(
                    FreightModel
                ).where(
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
    def _to_domain(
        model: FreightModel
    ) -> Freight:
        return Freight(
            freight_id=model.freight_id,
            customer_id=model.customer_id,
            primary_quote_id=(
                model.primary_quote_id
            ),
            created_at=model.created_at,
            created_by=model.created_by
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
