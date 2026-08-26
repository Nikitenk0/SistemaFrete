from sqlalchemy import and_, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from application.exceptions import VehiclePersistenceError
from application.ports.freight_vehicle_selection_repository import (
    FreightVehicleSelectionRepository,
)
from domain.models.vehicle import Vehicle, VehicleStatus, VehicleType
from infrastructure.persistence.sqlalchemy.models import (
    FreightModel,
    FreightTransportUnitModel,
    FreightVehicleRecordModel,
    VehicleModel,
)


class SqlAlchemyFreightVehicleSelectionRepository(
    FreightVehicleSelectionRepository
):

    def __init__(self, session: Session):
        self._session = session

    def search_available(
        self,
        query: str = "",
        limit: int = 200,
    ) -> tuple[Vehicle, ...]:
        active_use_exists = (
            select(FreightVehicleRecordModel.freight_vehicle_record_id)
            .join(
                FreightTransportUnitModel,
                FreightTransportUnitModel.freight_transport_unit_id
                == FreightVehicleRecordModel.freight_transport_unit_id,
            )
            .join(
                FreightModel,
                FreightModel.freight_id
                == FreightTransportUnitModel.freight_id,
            )
            .where(
                or_(
                    FreightVehicleRecordModel.vehicle_id
                    == VehicleModel.vehicle_id,
                    and_(
                        FreightVehicleRecordModel.vehicle_id.is_(None),
                        FreightVehicleRecordModel.plate == VehicleModel.plate,
                    ),
                ),
                FreightModel.current_status.in_(("PENDING", "IN_PROGRESS")),
            )
            .exists()
        )

        statement = select(VehicleModel).where(
            VehicleModel.status == VehicleStatus.ACTIVE.value,
            ~active_use_exists,
        )

        normalized_query = query.strip()
        if normalized_query:
            compact_query = "".join(
                character
                for character in normalized_query.upper()
                if character not in {"-", " "}
            )
            statement = statement.where(
                or_(
                    VehicleModel.plate.ilike(f"%{compact_query}%"),
                    VehicleModel.vehicle_type.ilike(
                        f"%{normalized_query.upper()}%"
                    ),
                )
            )

        statement = statement.order_by(
            VehicleModel.plate,
            VehicleModel.vehicle_id,
        ).limit(limit)

        try:
            models = self._session.scalars(statement).all()
        except SQLAlchemyError as error:
            raise VehiclePersistenceError(
                "Não foi possível pesquisar veículos disponíveis para o frete"
            ) from error

        return tuple(self._to_domain(model) for model in models)

    @staticmethod
    def _to_domain(model: VehicleModel) -> Vehicle:
        return Vehicle(
            vehicle_id=model.vehicle_id,
            plate=model.plate,
            vehicle_type=VehicleType(model.vehicle_type),
            status=VehicleStatus(model.status),
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
        )
