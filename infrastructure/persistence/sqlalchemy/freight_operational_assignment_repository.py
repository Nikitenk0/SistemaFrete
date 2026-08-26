from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from application.exceptions import (
    FreightOperationalAssignmentPersistenceError,
)
from application.ports.freight_operational_assignment_repository import (
    FreightOperationalAssignmentRepository,
)
from domain.models.freight_operational_assignment import (
    FreightOperationalAssignment,
)
from domain.models.vehicle import VehicleType
from infrastructure.persistence.sqlalchemy.models import (
    FreightDriverAssignmentModel,
    FreightOperationalAssignmentModel,
)


class SqlAlchemyFreightOperationalAssignmentRepository(
    FreightOperationalAssignmentRepository
):

    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def add(
        self,
        assignment: FreightOperationalAssignment,
    ) -> FreightOperationalAssignment:
        if (
            assignment.freight_operational_assignment_id
            is not None
        ):
            raise ValueError(
                "Contexto operacional já possui ID"
            )

        model = FreightOperationalAssignmentModel(
            freight_driver_assignment_id=(
                assignment.freight_driver_assignment_id
            ),
            transport_provider_id=(
                assignment.transport_provider_id
            ),
            vehicle_id=assignment.vehicle_id,
            provider_name_snapshot=(
                assignment.provider_name_snapshot
            ),
            provider_tax_document_snapshot=(
                assignment.provider_tax_document_snapshot
            ),
            driver_name_snapshot=(
                assignment.driver_name_snapshot
            ),
            driver_cpf_snapshot=(
                assignment.driver_cpf_snapshot
            ),
            vehicle_plate_snapshot=(
                assignment.vehicle_plate_snapshot
            ),
            vehicle_type_snapshot=(
                assignment.vehicle_type_snapshot.value
            ),
            created_by=assignment.created_by,
        )

        if assignment.created_at is not None:
            model.created_at = assignment.created_at

        self._session.add(model)

        try:
            self._session.flush()
            self._session.refresh(model)
        except IntegrityError as error:
            raise FreightOperationalAssignmentPersistenceError(
                "A participação do motorista já possui "
                "contexto operacional"
            ) from error
        except SQLAlchemyError as error:
            raise FreightOperationalAssignmentPersistenceError(
                "Não foi possível salvar o contexto operacional"
            ) from error

        return self._to_domain(model)

    def get_by_driver_assignment_id(
        self,
        freight_driver_assignment_id: int,
    ) -> FreightOperationalAssignment | None:
        try:
            model = self._session.scalar(
                select(FreightOperationalAssignmentModel)
                .where(
                    FreightOperationalAssignmentModel
                    .freight_driver_assignment_id
                    == freight_driver_assignment_id
                )
            )
        except SQLAlchemyError as error:
            raise FreightOperationalAssignmentPersistenceError(
                "Não foi possível consultar o contexto operacional"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def list_by_transport_unit_id(
        self,
        freight_transport_unit_id: int,
    ) -> tuple[FreightOperationalAssignment, ...]:
        try:
            models = self._session.scalars(
                select(FreightOperationalAssignmentModel)
                .join(
                    FreightDriverAssignmentModel,
                    FreightDriverAssignmentModel
                    .freight_driver_assignment_id
                    == FreightOperationalAssignmentModel
                    .freight_driver_assignment_id,
                )
                .where(
                    FreightDriverAssignmentModel
                    .freight_transport_unit_id
                    == freight_transport_unit_id
                )
                .order_by(
                    FreightDriverAssignmentModel.started_at,
                    FreightOperationalAssignmentModel
                    .freight_operational_assignment_id,
                )
            ).all()
        except SQLAlchemyError as error:
            raise FreightOperationalAssignmentPersistenceError(
                "Não foi possível consultar o histórico "
                "operacional da unidade"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    @staticmethod
    def _to_domain(
        model: FreightOperationalAssignmentModel,
    ) -> FreightOperationalAssignment:
        return FreightOperationalAssignment(
            freight_operational_assignment_id=(
                model.freight_operational_assignment_id
            ),
            freight_driver_assignment_id=(
                model.freight_driver_assignment_id
            ),
            transport_provider_id=(
                model.transport_provider_id
            ),
            vehicle_id=model.vehicle_id,
            provider_name_snapshot=(
                model.provider_name_snapshot
            ),
            provider_tax_document_snapshot=(
                model.provider_tax_document_snapshot
            ),
            driver_name_snapshot=(
                model.driver_name_snapshot
            ),
            driver_cpf_snapshot=(
                model.driver_cpf_snapshot
            ),
            vehicle_plate_snapshot=(
                model.vehicle_plate_snapshot
            ),
            vehicle_type_snapshot=VehicleType(
                model.vehicle_type_snapshot
            ),
            created_at=model.created_at,
            created_by=model.created_by,
        )
