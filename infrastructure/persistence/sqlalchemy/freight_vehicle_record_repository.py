from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError
)
from sqlalchemy.orm import Session

from application.exceptions import (
    FreightVehicleRecordPersistenceError,
    InvalidFreightStateError
)
from application.ports.freight_vehicle_record_repository import (
    FreightVehicleRecordRepository
)
from domain.models.freight_vehicle_record import (
    FreightVehicleRecord,
    FreightVehicleType
)
from infrastructure.persistence.sqlalchemy.models import (
    FreightTransportUnitModel,
    FreightVehicleRecordModel
)


class SqlAlchemyFreightVehicleRecordRepository(
    FreightVehicleRecordRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        vehicle_record: FreightVehicleRecord
    ) -> FreightVehicleRecord:

        if vehicle_record.freight_vehicle_record_id is not None:
            raise ValueError(
                "Veículo operacional já possui id"
            )

        model = self._to_model(
            vehicle_record
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
            raise FreightVehicleRecordPersistenceError(
                "Não foi possível salvar o veículo operacional"
            ) from error

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        freight_vehicle_record_id: int
    ) -> FreightVehicleRecord | None:

        return self._get_one(
            select(
                FreightVehicleRecordModel
            ).where(
                FreightVehicleRecordModel
                .freight_vehicle_record_id
                == freight_vehicle_record_id
            )
        )

    def get_by_transport_unit_id(
        self,
        freight_transport_unit_id: int
    ) -> FreightVehicleRecord | None:

        return self._get_one(
            select(
                FreightVehicleRecordModel
            ).where(
                FreightVehicleRecordModel
                .freight_transport_unit_id
                == freight_transport_unit_id
            )
        )

    def list_by_freight_id(
        self,
        freight_id: int
    ) -> tuple[FreightVehicleRecord, ...]:

        try:
            models = self._session.scalars(
                select(
                    FreightVehicleRecordModel
                )
                .join(
                    FreightTransportUnitModel,
                    FreightTransportUnitModel
                    .freight_transport_unit_id
                    == FreightVehicleRecordModel
                    .freight_transport_unit_id
                )
                .where(
                    FreightTransportUnitModel.freight_id
                    == freight_id
                )
                .order_by(
                    FreightTransportUnitModel.position,
                    FreightVehicleRecordModel
                    .freight_vehicle_record_id
                )
            ).all()

        except SQLAlchemyError as error:
            raise FreightVehicleRecordPersistenceError(
                "Não foi possível consultar os veículos operacionais"
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
    ) -> FreightVehicleRecord | None:

        try:
            model = self._session.scalar(
                statement
            )

        except SQLAlchemyError as error:
            raise FreightVehicleRecordPersistenceError(
                "Não foi possível consultar o veículo operacional"
            ) from error

        if model is None:
            return None

        return self._to_domain(
            model
        )

    @staticmethod
    def _to_model(
        vehicle_record: FreightVehicleRecord
    ) -> FreightVehicleRecordModel:

        model = FreightVehicleRecordModel(
            freight_transport_unit_id=(
                vehicle_record.freight_transport_unit_id
            ),
            vehicle_type=vehicle_record.vehicle_type.value,
            plate=vehicle_record.plate,
            axle_count=vehicle_record.axle_count,
            pallet_capacity_min=(
                vehicle_record.pallet_capacity_min
            ),
            pallet_capacity_max=(
                vehicle_record.pallet_capacity_max
            ),
            payload_capacity_kg=(
                vehicle_record.payload_capacity_kg
            ),
            created_by=vehicle_record.created_by
        )

        if vehicle_record.created_at is not None:
            model.created_at = vehicle_record.created_at

        return model

    @staticmethod
    def _to_domain(
        model: FreightVehicleRecordModel
    ) -> FreightVehicleRecord:

        return FreightVehicleRecord(
            freight_vehicle_record_id=(
                model.freight_vehicle_record_id
            ),
            freight_transport_unit_id=(
                model.freight_transport_unit_id
            ),
            vehicle_type=FreightVehicleType(
                model.vehicle_type
            ),
            plate=model.plate,
            axle_count=model.axle_count,
            pallet_capacity_min=(
                model.pallet_capacity_min
            ),
            pallet_capacity_max=(
                model.pallet_capacity_max
            ),
            payload_capacity_kg=(
                model.payload_capacity_kg
            ),
            created_at=model.created_at,
            created_by=model.created_by
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
            == (
                "uq_freight_vehicle_records_"
                "freight_transport_unit_id"
            )
        ):
            raise InvalidFreightStateError(
                "A unidade de transporte já possui "
                "veículo operacional registrado"
            ) from error

        raise FreightVehicleRecordPersistenceError(
            "Não foi possível salvar o veículo operacional"
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
