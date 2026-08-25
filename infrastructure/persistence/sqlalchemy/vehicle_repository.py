from sqlalchemy import (
    or_,
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
    VehicleAlreadyExistsError,
    VehiclePersistenceError
)
from application.ports.vehicle_repository import (
    VehicleRepository
)
from domain.models.vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
    normalize_vehicle_plate
)
from infrastructure.persistence.sqlalchemy.models import (
    VehicleModel
)


class SqlAlchemyVehicleRepository(
    VehicleRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        vehicle: Vehicle
    ) -> Vehicle:

        if vehicle.vehicle_id is not None:
            raise ValueError(
                "Veículo já possui vehicle_id"
            )

        model = self._to_model(
            vehicle
        )
        self._session.add(
            model
        )

        try:
            self._session.flush()
            self._session.refresh(
                model
            )
        except IntegrityError as error:
            self._raise_integrity_error(
                error
            )
        except SQLAlchemyError as error:
            raise VehiclePersistenceError(
                "Não foi possível salvar o veículo"
            ) from error

        return self._to_domain(
            model
        )

    def save(
        self,
        vehicle: Vehicle
    ) -> Vehicle:

        if vehicle.vehicle_id is None:
            raise ValueError(
                "Veículo precisa possuir vehicle_id"
            )

        try:
            model = self._session.scalar(
                select(
                    VehicleModel
                )
                .where(
                    VehicleModel.vehicle_id
                    == vehicle.vehicle_id
                )
                .with_for_update()
            )

            if model is None:
                raise VehiclePersistenceError(
                    "Veículo não encontrado durante atualização"
                )

            model.plate = vehicle.plate
            model.vehicle_type = vehicle.vehicle_type.value
            model.status = vehicle.status.value
            model.updated_by = vehicle.updated_by

            if vehicle.updated_at is not None:
                model.updated_at = vehicle.updated_at

            self._session.flush()
            self._session.refresh(
                model
            )

        except IntegrityError as error:
            self._raise_integrity_error(
                error
            )
        except VehiclePersistenceError:
            raise
        except SQLAlchemyError as error:
            raise VehiclePersistenceError(
                "Não foi possível atualizar o veículo"
            ) from error

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        vehicle_id: int
    ) -> Vehicle | None:
        return self._get_by_id(
            vehicle_id,
            for_update=False
        )

    def get_by_id_for_update(
        self,
        vehicle_id: int
    ) -> Vehicle | None:
        return self._get_by_id(
            vehicle_id,
            for_update=True
        )

    def _get_by_id(
        self,
        vehicle_id: int,
        for_update: bool
    ) -> Vehicle | None:

        statement = select(
            VehicleModel
        ).where(
            VehicleModel.vehicle_id
            == vehicle_id
        )

        if for_update:
            statement = statement.with_for_update()

        try:
            model = self._session.scalar(
                statement
            )
        except SQLAlchemyError as error:
            raise VehiclePersistenceError(
                "Não foi possível consultar o veículo"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def get_by_plate(
        self,
        plate: str
    ) -> Vehicle | None:

        try:
            normalized_plate = normalize_vehicle_plate(
                plate
            )
        except ValueError:
            return None

        try:
            model = self._session.scalar(
                select(
                    VehicleModel
                ).where(
                    VehicleModel.plate
                    == normalized_plate
                )
            )
        except SQLAlchemyError as error:
            raise VehiclePersistenceError(
                "Não foi possível consultar veículo pela placa"
            ) from error

        return (
            self._to_domain(model)
            if model is not None
            else None
        )

    def search(
        self,
        query: str = "",
        status: VehicleStatus | None = None,
        vehicle_type: VehicleType | None = None,
        limit: int = 100
    ) -> tuple[Vehicle, ...]:

        statement = select(
            VehicleModel
        )

        query = query.strip()
        if query:
            compact_query = "".join(
                character
                for character in query.upper()
                if character not in {"-", " "}
            )
            statement = statement.where(
                or_(
                    VehicleModel.plate.ilike(
                        f"%{compact_query}%"
                    ),
                    VehicleModel.vehicle_type.ilike(
                        f"%{query.upper()}%"
                    )
                )
            )

        if status is not None:
            statement = statement.where(
                VehicleModel.status
                == status.value
            )

        if vehicle_type is not None:
            statement = statement.where(
                VehicleModel.vehicle_type
                == vehicle_type.value
            )

        statement = statement.order_by(
            VehicleModel.plate,
            VehicleModel.vehicle_id
        ).limit(
            limit
        )

        try:
            models = self._session.scalars(
                statement
            ).all()
        except SQLAlchemyError as error:
            raise VehiclePersistenceError(
                "Não foi possível pesquisar veículos"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )

    @staticmethod
    def _to_model(
        vehicle: Vehicle
    ) -> VehicleModel:

        model = VehicleModel(
            plate=vehicle.plate,
            vehicle_type=vehicle.vehicle_type.value,
            status=vehicle.status.value,
            created_by=vehicle.created_by,
            updated_by=vehicle.updated_by
        )

        if vehicle.created_at is not None:
            model.created_at = vehicle.created_at

        if vehicle.updated_at is not None:
            model.updated_at = vehicle.updated_at

        return model

    @staticmethod
    def _to_domain(
        model: VehicleModel
    ) -> Vehicle:
        return Vehicle(
            vehicle_id=model.vehicle_id,
            plate=model.plate,
            vehicle_type=VehicleType(
                model.vehicle_type
            ),
            status=VehicleStatus(
                model.status
            ),
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by
        )

    @staticmethod
    def _raise_integrity_error(
        error: IntegrityError
    ) -> None:

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
        constraint_name = getattr(
            diagnostics,
            "constraint_name",
            None
        )

        if constraint_name == "uq_vehicles_plate":
            raise VehicleAlreadyExistsError(
                "Placa já cadastrada para outro veículo"
            ) from error

        raise VehiclePersistenceError(
            "Não foi possível salvar o veículo"
        ) from error
