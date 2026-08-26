from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from application.dtos.freight_driver_selection import (
    FreightDriverSelectionItem,
)
from application.exceptions import DriverPersistenceError
from application.ports.freight_driver_selection_repository import (
    FreightDriverSelectionRepository,
)
from domain.models.driver import DriverStatus
from infrastructure.persistence.sqlalchemy.models import (
    DriverModel,
    FreightDriverAssignmentModel,
)


class SqlAlchemyFreightDriverSelectionRepository(
    FreightDriverSelectionRepository
):

    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def search_available(
        self,
        query: str,
        limit: int = 20,
    ) -> tuple[FreightDriverSelectionItem, ...]:

        normalized_digits = "".join(
            character
            for character in query
            if character.isdigit()
        )

        conditions = [
            DriverModel.name.ilike(
                f"%{query}%"
            ),
            DriverModel.rg.ilike(
                f"%{query}%"
            ),
            DriverModel.cnh_number.ilike(
                f"%{query}%"
            ),
        ]

        if normalized_digits:
            conditions.append(
                DriverModel.cpf.contains(
                    normalized_digits
                )
            )

        active_assignment_exists = (
            select(
                FreightDriverAssignmentModel
                .freight_driver_assignment_id
            )
            .where(
                FreightDriverAssignmentModel.driver_id
                == DriverModel.driver_id,
                FreightDriverAssignmentModel.ended_at.is_(
                    None
                ),
            )
            .exists()
        )

        statement = (
            select(
                DriverModel.driver_id.label(
                    "driver_id"
                ),
                DriverModel.name.label(
                    "name"
                ),
                DriverModel.cpf.label(
                    "cpf"
                ),
                DriverModel.cnh_number.label(
                    "cnh_number"
                ),
                DriverModel.cnh_category.label(
                    "cnh_category"
                ),
            )
            .where(
                DriverModel.status
                == DriverStatus.ACTIVE.value,
                ~active_assignment_exists,
                or_(*conditions),
            )
            .order_by(
                DriverModel.name,
                DriverModel.driver_id,
            )
            .limit(limit)
        )

        try:
            rows = (
                self._session.execute(statement)
                .mappings()
                .all()
            )
        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível pesquisar motoristas disponíveis"
            ) from error

        return tuple(
            FreightDriverSelectionItem(
                driver_id=row["driver_id"],
                name=row["name"],
                cpf=row["cpf"],
                cnh_number=row["cnh_number"],
                cnh_category=row["cnh_category"],
            )
            for row in rows
        )
