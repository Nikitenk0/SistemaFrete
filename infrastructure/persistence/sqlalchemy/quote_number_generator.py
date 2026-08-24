from sqlalchemy.dialects.postgresql import (
    insert
)
from sqlalchemy.exc import (
    SQLAlchemyError
)
from sqlalchemy.orm import (
    Session
)

from application.exceptions import (
    QuoteNumberGenerationError
)
from application.ports.quote_number_generator import (
    QuoteNumberGenerator
)
from infrastructure.persistence.sqlalchemy.models import (
    QuoteNumberCounterModel
)


class PostgreSQLQuoteNumberGenerator(
    QuoteNumberGenerator
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def next_number(
        self,
        year: int
    ) -> str:

        if year < 1 or year > 9999:
            raise QuoteNumberGenerationError(
                "Ano inválido para numeração "
                "do orçamento"
            )

        statement = (
            insert(
                QuoteNumberCounterModel
            )
            .values(
                year=year,
                last_value=1
            )
            .on_conflict_do_update(
                index_elements=[
                    QuoteNumberCounterModel.year
                ],
                set_={
                    "last_value": (
                        QuoteNumberCounterModel
                        .last_value
                        + 1
                    )
                }
            )
            .returning(
                QuoteNumberCounterModel.last_value
            )
        )

        try:

            sequence_number = (
                self._session.scalar(
                    statement
                )
            )

        except SQLAlchemyError as error:

            raise QuoteNumberGenerationError(
                "Não foi possível gerar "
                "o número do orçamento"
            ) from error

        if sequence_number is None:
            raise QuoteNumberGenerationError(
                "Não foi possível obter "
                "o número do orçamento"
            )

        return (
            f"ORC-{year:04d}-"
            f"{sequence_number:05d}"
        )