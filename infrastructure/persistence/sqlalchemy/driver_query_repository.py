from sqlalchemy import (
    and_,
    or_,
    select
)
from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session,
    aliased
)

from application.dtos.driver_query import (
    DriverListItem
)
from application.exceptions import (
    DriverPersistenceError
)
from application.ports.driver_query_repository import (
    DriverQueryRepository
)
from domain.models.driver import (
    DriverStatus
)
from infrastructure.persistence.sqlalchemy.models import (
    DriverContactModel,
    DriverModel
)


class SqlAlchemyDriverQueryRepository(
    DriverQueryRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def list(
        self,
        query: str = "",
        status: DriverStatus | None = None,
        limit: int = 100
    ) -> tuple[DriverListItem, ...]:

        primary_contact = aliased(
            DriverContactModel
        )

        statement = (
            select(
                DriverModel.driver_id,
                DriverModel.name,
                DriverModel.cpf,
                DriverModel.cnh_number,
                DriverModel.cnh_category,
                DriverModel.cnh_expiration_date,
                DriverModel.status,
                primary_contact.phone,
                primary_contact.email
            )
            .outerjoin(
                primary_contact,
                and_(
                    primary_contact.driver_id
                    == DriverModel.driver_id,
                    primary_contact.is_primary.is_(
                        True
                    )
                )
            )
        )

        normalized_query = query.strip()

        if normalized_query:
            normalized_cpf = self._normalize_cpf(
                normalized_query
            )

            conditions = [
                DriverModel.name.ilike(
                    f"%{normalized_query}%"
                ),
                DriverModel.rg.ilike(
                    f"%{normalized_query}%"
                ),
                DriverModel.cnh_number.ilike(
                    f"%{normalized_query}%"
                )
            ]

            if normalized_cpf:
                conditions.append(
                    DriverModel.cpf.contains(
                        normalized_cpf
                    )
                )

            statement = statement.where(
                or_(
                    *conditions
                )
            )

        if status is not None:
            statement = statement.where(
                DriverModel.status
                == status.value
            )

        statement = statement.order_by(
            DriverModel.name,
            DriverModel.driver_id
        ).limit(
            limit
        )

        try:
            rows = self._session.execute(
                statement
            ).all()
        except SQLAlchemyError as error:
            raise DriverPersistenceError(
                "Não foi possível consultar motoristas"
            ) from error

        return tuple(
            DriverListItem(
                driver_id=row.driver_id,
                name=row.name,
                cpf=row.cpf,
                cnh_number=row.cnh_number,
                cnh_category=row.cnh_category,
                cnh_expiration_date=(
                    row.cnh_expiration_date
                ),
                status=DriverStatus(
                    row.status
                ),
                primary_phone=row.phone,
                primary_email=row.email
            )
            for row in rows
        )

    @staticmethod
    def _normalize_cpf(
        value: str
    ) -> str:
        return "".join(
            character
            for character in value
            if character.isdigit()
        )
