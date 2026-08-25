from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)
from sqlalchemy.orm import Session

from application.exceptions import (
    FreightDriverAssignmentNotFoundError,
    FreightDriverAssignmentPersistenceError,
    InvalidFreightStateError
)
from application.ports.freight_driver_assignment_repository import (
    FreightDriverAssignmentRepository
)
from domain.models.freight_driver_assignment import (
    FreightDriverAssignment
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightDriverAssignmentModel,
    FreightTransportUnitModel
)


class SqlAlchemyFreightDriverAssignmentRepository(
    FreightDriverAssignmentRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        assignment: FreightDriverAssignment
    ) -> FreightDriverAssignment:

        if assignment.freight_driver_assignment_id is not None:
            raise ValueError(
                "Participação de motorista já possui id"
            )

        model = self._to_model(
            assignment
        )

        self._session.add(
            model
        )

        try:
            self._session.flush()

        except IntegrityError as error:
            self._raise_integrity_error(
                error
            )

        except SQLAlchemyError as error:
            raise FreightDriverAssignmentPersistenceError(
                "Não foi possível salvar a participação "
                "de motorista"
            ) from error

        return self._to_domain(
            model
        )

    def save(
        self,
        assignment: FreightDriverAssignment
    ) -> FreightDriverAssignment:

        assignment_id = (
            assignment.freight_driver_assignment_id
        )

        if assignment_id is None:
            raise ValueError(
                "Participação de motorista não possui id"
            )

        try:
            model = self._session.scalar(
                select(
                    FreightDriverAssignmentModel
                ).where(
                    FreightDriverAssignmentModel
                    .freight_driver_assignment_id
                    == assignment_id
                )
            )

            if model is None:
                raise FreightDriverAssignmentNotFoundError(
                    "Participação de motorista não encontrada"
                )

            self._validate_immutable_fields(
                model,
                assignment
            )

            model.ended_at = assignment.ended_at
            model.actual_driver_amount = (
                assignment.actual_driver_amount
            )
            model.updated_at = assignment.updated_at
            model.updated_by = assignment.updated_by

            self._session.flush()

        except FreightDriverAssignmentNotFoundError:
            raise

        except IntegrityError as error:
            self._raise_integrity_error(
                error
            )

        except SQLAlchemyError as error:
            raise FreightDriverAssignmentPersistenceError(
                "Não foi possível atualizar a participação "
                "de motorista"
            ) from error

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        freight_driver_assignment_id: int
    ) -> FreightDriverAssignment | None:

        return self._get_one(
            select(
                FreightDriverAssignmentModel
            ).where(
                FreightDriverAssignmentModel
                .freight_driver_assignment_id
                == freight_driver_assignment_id
            )
        )

    def get_active_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightDriverAssignment | None:

        return self._get_one(
            select(
                FreightDriverAssignmentModel
            ).where(
                FreightDriverAssignmentModel
                .freight_transport_unit_id
                == freight_transport_unit_id,
                FreightDriverAssignmentModel.ended_at
                .is_(None)
            )
        )

    def get_active_by_driver_id(
        self,
        driver_id: int
    ) -> FreightDriverAssignment | None:

        return self._get_one(
            select(
                FreightDriverAssignmentModel
            ).where(
                FreightDriverAssignmentModel.driver_id
                == driver_id,
                FreightDriverAssignmentModel.ended_at
                .is_(None)
            )
        )

    def list_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> tuple[FreightDriverAssignment, ...]:

        try:
            models = self._session.scalars(
                select(
                    FreightDriverAssignmentModel
                )
                .where(
                    FreightDriverAssignmentModel
                    .freight_transport_unit_id
                    == freight_transport_unit_id
                )
                .order_by(
                    FreightDriverAssignmentModel.started_at,
                    FreightDriverAssignmentModel
                    .freight_driver_assignment_id
                )
            ).all()

        except SQLAlchemyError as error:
            raise FreightDriverAssignmentPersistenceError(
                "Não foi possível consultar as participações "
                "de motorista"
            ) from error

        return tuple(
            self._to_domain(
                model
            )
            for model in models
        )

    def list_active_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightDriverAssignment, ...]:

        try:
            models = self._session.scalars(
                select(
                    FreightDriverAssignmentModel
                )
                .join(
                    FreightTransportUnitModel,
                    FreightTransportUnitModel
                    .freight_transport_unit_id
                    == FreightDriverAssignmentModel
                    .freight_transport_unit_id
                )
                .where(
                    FreightTransportUnitModel.freight_id
                    == freight_id,
                    FreightDriverAssignmentModel.ended_at
                    .is_(None)
                )
                .order_by(
                    FreightTransportUnitModel.position,
                    FreightDriverAssignmentModel.started_at,
                    FreightDriverAssignmentModel
                    .freight_driver_assignment_id
                )
            ).all()

        except SQLAlchemyError as error:
            raise FreightDriverAssignmentPersistenceError(
                "Não foi possível consultar os motoristas "
                "ativos do frete"
            ) from error

        return tuple(
            self._to_domain(
                model
            )
            for model in models
        )

    def _get_one(
        self,
        statement
    ) -> FreightDriverAssignment | None:

        try:
            model = self._session.scalar(
                statement
            )

        except SQLAlchemyError as error:
            raise FreightDriverAssignmentPersistenceError(
                "Não foi possível consultar a participação "
                "de motorista"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    @staticmethod
    def _to_model(
        assignment: FreightDriverAssignment
    ) -> FreightDriverAssignmentModel:

        model = FreightDriverAssignmentModel(
            freight_transport_unit_id=(
                assignment.freight_transport_unit_id
            ),
            driver_id=assignment.driver_id,
            started_at=assignment.started_at,
            ended_at=assignment.ended_at,
            actual_driver_amount=(
                assignment.actual_driver_amount
            ),
            created_by=assignment.created_by,
            updated_by=assignment.updated_by
        )

        if assignment.created_at is not None:
            model.created_at = assignment.created_at

        if assignment.updated_at is not None:
            model.updated_at = assignment.updated_at

        return model

    @staticmethod
    def _to_domain(
        model: FreightDriverAssignmentModel
    ) -> FreightDriverAssignment:

        return FreightDriverAssignment(
            freight_driver_assignment_id=(
                model.freight_driver_assignment_id
            ),
            freight_transport_unit_id=(
                model.freight_transport_unit_id
            ),
            driver_id=model.driver_id,
            started_at=model.started_at,
            ended_at=model.ended_at,
            actual_driver_amount=(
                model.actual_driver_amount
            ),
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by
        )

    @staticmethod
    def _validate_immutable_fields(
        model: FreightDriverAssignmentModel,
        assignment: FreightDriverAssignment
    ) -> None:

        if (
            model.freight_transport_unit_id
            != assignment.freight_transport_unit_id
            or model.driver_id != assignment.driver_id
            or model.started_at != assignment.started_at
            or model.created_at != assignment.created_at
            or model.created_by != assignment.created_by
        ):
            raise ValueError(
                "Campos de origem da participação de "
                "motorista são imutáveis"
            )

    @classmethod
    def _raise_integrity_error(
        cls,
        error: IntegrityError
    ) -> None:

        constraint_name = cls._get_constraint_name(
            error
        )

        if (
            constraint_name
            == "uq_freight_driver_assignments_active_unit"
        ):
            raise InvalidFreightStateError(
                "Unidade de transporte já possui motorista ativo"
            ) from error

        if (
            constraint_name
            == "uq_freight_driver_assignments_active_driver"
        ):
            raise InvalidFreightStateError(
                "Motorista já possui participação operacional ativa"
            ) from error

        raise FreightDriverAssignmentPersistenceError(
            "Não foi possível salvar a participação de motorista"
        ) from error

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
