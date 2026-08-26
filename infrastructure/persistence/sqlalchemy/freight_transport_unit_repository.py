from sqlalchemy import (
    func,
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
    FreightPersistenceError
)
from application.ports.freight_transport_unit_repository import (
    FreightTransportUnitRepository
)
from domain.models.freight_transport_unit import (
    FreightTransportUnit
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightTransportUnitModel
)


class SqlAlchemyFreightTransportUnitRepository(
    FreightTransportUnitRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        transport_unit: FreightTransportUnit
    ) -> FreightTransportUnit:

        if (
            transport_unit.freight_transport_unit_id
            is not None
        ):
            raise ValueError(
                "Unidade de transporte já possui id"
            )

        model = self._to_model(
            transport_unit
        )

        self._session.add(
            model
        )

        try:
            self._session.flush()

        except IntegrityError as error:

            constraint_name = (
                self._get_constraint_name(
                    error
                )
            )

            if (
                constraint_name
                == (
                    "uq_freight_transport_units_"
                    "freight_id_position"
                )
            ):
                raise FreightPersistenceError(
                    "Já existe unidade de transporte "
                    "nessa posição para o frete"
                ) from error

            raise FreightPersistenceError(
                "Não foi possível salvar a unidade "
                "de transporte do frete"
            ) from error

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível salvar a unidade "
                "de transporte do frete"
            ) from error

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightTransportUnit | None:

        try:
            model = self._session.scalar(
                select(
                    FreightTransportUnitModel
                ).where(
                    FreightTransportUnitModel.freight_transport_unit_id
                    == freight_transport_unit_id
                )
            )

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar a unidade "
                "de transporte do frete"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightTransportUnit, ...]:

        try:
            models = self._session.scalars(
                select(
                    FreightTransportUnitModel
                )
                .where(
                    FreightTransportUnitModel.freight_id
                    == freight_id
                )
                .order_by(
                    FreightTransportUnitModel.position
                )
            ).all()

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar as unidades "
                "de transporte do frete"
            ) from error

        return tuple(
            self._to_domain(
                model
            )
            for model in models
        )

    def count_by_freight_id(
        self,
        freight_id: int
    ) -> int:

        try:
            result = self._session.scalar(
                select(
                    func.count(
                        FreightTransportUnitModel
                        .freight_transport_unit_id
                    )
                ).where(
                    FreightTransportUnitModel.freight_id
                    == freight_id
                )
            )

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível contar as unidades "
                "de transporte do frete"
            ) from error

        return int(
            result or 0
        )

    def delete_by_id(
        self,
        freight_transport_unit_id: int
    ) -> None:
        try:
            model = self._session.get(
                FreightTransportUnitModel,
                freight_transport_unit_id
            )

            if model is None:
                return

            self._session.delete(model)
            self._session.flush()

        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível remover a unidade "
                "de transporte do frete"
            ) from error

    @staticmethod
    def _to_model(
        transport_unit: FreightTransportUnit
    ) -> FreightTransportUnitModel:

        model = FreightTransportUnitModel(
            freight_id=transport_unit.freight_id,
            position=transport_unit.position,
            created_by=transport_unit.created_by
        )

        if transport_unit.created_at is not None:
            model.created_at = (
                transport_unit.created_at
            )

        return model

    @staticmethod
    def _to_domain(
        model: FreightTransportUnitModel
    ) -> FreightTransportUnit:

        return FreightTransportUnit(
            freight_transport_unit_id=(
                model.freight_transport_unit_id
            ),
            freight_id=model.freight_id,
            position=model.position,
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
