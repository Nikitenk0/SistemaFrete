from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, aliased

from application.dtos.freight_query import (
    FreightDetails,
    FreightListItem,
    FreightQueryFilters,
)
from application.exceptions import FreightPersistenceError
from application.ports.freight_query_repository import (
    FreightQueryRepository,
)
from domain.models.freight import FreightStatus
from domain.models.quote import QuoteStatus, QuoteType
from infrastructure.persistence.sqlalchemy.models import (
    FreightFinancialResultModel,
    FreightModel,
    QuoteModel,
    QuoteVersionModel,
)


class SqlAlchemyFreightQueryRepository(
    FreightQueryRepository
):

    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def list(
        self,
        filters: FreightQueryFilters,
    ) -> tuple[FreightListItem, ...]:

        statement = self._base_statement()

        if filters.customer_id is not None:
            statement = statement.where(
                FreightModel.customer_id
                == filters.customer_id
            )

        if filters.status is not None:
            statement = statement.where(
                FreightModel.current_status
                == filters.status.value
            )

        if filters.completed_from is not None:
            statement = statement.where(
                FreightModel.completed_at
                >= filters.completed_from
            )

        if filters.completed_to is not None:
            statement = statement.where(
                FreightModel.completed_at
                <= filters.completed_to
            )

        statement = statement.order_by(
            FreightModel.created_at.desc(),
            FreightModel.freight_id.desc(),
        )

        try:
            rows = (
                self._session.execute(statement)
                .mappings()
                .all()
            )
        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar a lista de fretes"
            ) from error

        return tuple(
            self._to_list_item(row)
            for row in rows
        )

    def get_by_id(
        self,
        freight_id: int,
    ) -> FreightDetails | None:

        statement = self._base_statement().where(
            FreightModel.freight_id == freight_id
        )

        try:
            row = (
                self._session.execute(statement)
                .mappings()
                .one_or_none()
            )
        except SQLAlchemyError as error:
            raise FreightPersistenceError(
                "Não foi possível consultar os detalhes do frete"
            ) from error

        if row is None:
            return None

        return self._to_details(row)

    @staticmethod
    def _base_statement():
        primary_quote = aliased(
            QuoteModel,
            name="primary_quote",
        )
        primary_version = aliased(
            QuoteVersionModel,
            name="primary_version",
        )
        approved_quote = aliased(
            QuoteModel,
            name="approved_quote",
        )
        approved_version = aliased(
            QuoteVersionModel,
            name="approved_version",
        )

        contracted_revenue = (
            select(
                func.coalesce(
                    func.sum(
                        approved_version.contracted_price
                    ),
                    Decimal("0"),
                )
            )
            .select_from(approved_quote)
            .join(
                approved_version,
                and_(
                    approved_version.quote_id
                    == approved_quote.quote_id,
                    approved_version.quote_version_id
                    == approved_quote.approved_version_id,
                ),
            )
            .where(
                approved_quote.freight_id
                == FreightModel.freight_id,
                approved_quote.current_status
                == QuoteStatus.APPROVED.value,
            )
            .correlate(FreightModel)
            .scalar_subquery()
        )

        approved_complementary_quote_count = (
            select(
                func.count(
                    approved_quote.quote_id
                )
            )
            .select_from(approved_quote)
            .where(
                approved_quote.freight_id
                == FreightModel.freight_id,
                approved_quote.current_status
                == QuoteStatus.APPROVED.value,
                approved_quote.quote_type
                == QuoteType.COMPLEMENTARY.value,
            )
            .correlate(FreightModel)
            .scalar_subquery()
        )

        customer_name = func.coalesce(
            primary_version.customer_trade_name_snapshot,
            primary_version.customer_legal_name_snapshot,
        )

        return (
            select(
                FreightModel.freight_id.label(
                    "freight_id"
                ),
                FreightModel.customer_id.label(
                    "customer_id"
                ),
                primary_quote.quote_id.label(
                    "primary_quote_id"
                ),
                primary_quote.quote_number.label(
                    "primary_quote_number"
                ),
                primary_version.customer_legal_name_snapshot.label(
                    "customer_legal_name"
                ),
                primary_version.customer_trade_name_snapshot.label(
                    "customer_trade_name"
                ),
                customer_name.label(
                    "customer_name"
                ),
                primary_version.origin.label(
                    "origin"
                ),
                primary_version.destination.label(
                    "destination"
                ),
                FreightModel.current_status.label(
                    "current_status"
                ),
                contracted_revenue.label(
                    "contracted_revenue"
                ),
                approved_complementary_quote_count.label(
                    "approved_complementary_quote_count"
                ),
                FreightFinancialResultModel
                .freight_financial_result_id.label(
                    "financial_result_id"
                ),
                FreightModel.created_at.label(
                    "created_at"
                ),
                FreightModel.started_at.label(
                    "started_at"
                ),
                FreightModel.completed_at.label(
                    "completed_at"
                ),
                FreightModel.cancelled_at.label(
                    "cancelled_at"
                ),
            )
            .select_from(FreightModel)
            .join(
                primary_quote,
                and_(
                    primary_quote.quote_id
                    == FreightModel.primary_quote_id,
                    primary_quote.quote_type
                    == QuoteType.PRIMARY.value,
                ),
            )
            .join(
                primary_version,
                and_(
                    primary_version.quote_id
                    == primary_quote.quote_id,
                    primary_version.quote_version_id
                    == primary_quote.approved_version_id,
                ),
            )
            .outerjoin(
                FreightFinancialResultModel,
                FreightFinancialResultModel.freight_id
                == FreightModel.freight_id,
            )
        )

    @classmethod
    def _to_list_item(
        cls,
        row,
    ) -> FreightListItem:
        return FreightListItem(
            freight_id=row["freight_id"],
            customer_id=row["customer_id"],
            customer_name=cls._required_text(
                row["customer_name"],
                "identificação histórica do cliente",
            ),
            primary_quote_id=row["primary_quote_id"],
            primary_quote_number=cls._required_text(
                row["primary_quote_number"],
                "número do orçamento principal",
            ),
            origin=cls._required_text(
                row["origin"],
                "origem",
            ),
            destination=cls._required_text(
                row["destination"],
                "destino",
            ),
            current_status=FreightStatus(
                row["current_status"]
            ),
            contracted_revenue=cls._decimal(
                row["contracted_revenue"]
            ),
            financially_closed=(
                row["financial_result_id"] is not None
            ),
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            cancelled_at=row["cancelled_at"],
        )

    @classmethod
    def _to_details(
        cls,
        row,
    ) -> FreightDetails:
        return FreightDetails(
            freight_id=row["freight_id"],
            customer_id=row["customer_id"],
            customer_legal_name=row[
                "customer_legal_name"
            ],
            customer_trade_name=row[
                "customer_trade_name"
            ],
            primary_quote_id=row["primary_quote_id"],
            primary_quote_number=cls._required_text(
                row["primary_quote_number"],
                "número do orçamento principal",
            ),
            origin=cls._required_text(
                row["origin"],
                "origem",
            ),
            destination=cls._required_text(
                row["destination"],
                "destino",
            ),
            current_status=FreightStatus(
                row["current_status"]
            ),
            contracted_revenue=cls._decimal(
                row["contracted_revenue"]
            ),
            approved_complementary_quote_count=(
                row[
                    "approved_complementary_quote_count"
                ]
            ),
            financially_closed=(
                row["financial_result_id"] is not None
            ),
            financial_result_id=row[
                "financial_result_id"
            ],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            cancelled_at=row["cancelled_at"],
        )

    @staticmethod
    def _required_text(
        value: str | None,
        field_name: str,
    ) -> str:
        if value is None or not value.strip():
            raise FreightPersistenceError(
                "Consulta de frete retornou "
                f"{field_name} ausente"
            )
        return value.strip()

    @staticmethod
    def _decimal(value) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
