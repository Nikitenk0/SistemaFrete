from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from application.exceptions import QuotePersistenceError
from application.ports.freight_financial_quote_repository import (
    FreightFinancialQuoteRepository
)
from domain.models.quote import Quote
from infrastructure.persistence.sqlalchemy.models import QuoteModel
from infrastructure.persistence.sqlalchemy.quote_repository import (
    SqlAlchemyQuoteRepository
)


class SqlAlchemyFreightFinancialQuoteRepository(
    SqlAlchemyQuoteRepository,
    FreightFinancialQuoteRepository
):

    def list_by_freight_id_for_update(
        self,
        freight_id: int
    ) -> tuple[Quote, ...]:

        try:
            models = self._session.scalars(
                select(
                    QuoteModel
                )
                .options(
                    *self._load_options()
                )
                .where(
                    QuoteModel.freight_id
                    == freight_id
                )
                .order_by(
                    QuoteModel.quote_id
                )
                .with_for_update()
            ).all()

        except SQLAlchemyError as error:
            raise QuotePersistenceError(
                "Não foi possível bloquear os orçamentos do frete "
                "para fechamento financeiro"
            ) from error

        return tuple(
            self._to_domain(model)
            for model in models
        )
