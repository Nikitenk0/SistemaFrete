from sqlalchemy import select
from sqlalchemy.orm import (
    Session,
    selectinload
)

from application.ports.quote_repository import (
    QuoteRepository
)
from domain.models.calculated_tax import (
    CalculatedTax
)
from domain.models.quote import Quote
from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from infrastructure.persistence.sqlalchemy.models import (
    QuoteModel,
    QuoteTaxModel
)


class SqlAlchemyQuoteRepository(
    QuoteRepository
):

    def __init__(
        self,
        session: Session
    ):
        self._session = session

    def add(
        self,
        quote: Quote
    ) -> Quote:

        if quote.quote_id is not None:
            raise ValueError(
                "Orçamento já possui quote_id"
            )

        model = self._to_model(
            quote
        )

        self._session.add(
            model
        )

        self._session.flush()

        self._session.refresh(
            model
        )

        return self._to_domain(
            model
        )

    def get_by_id(
        self,
        quote_id: int
    ) -> Quote | None:

        model = self._session.scalar(
            select(
                QuoteModel
            )
            .options(
                selectinload(
                    QuoteModel.taxes
                )
            )
            .where(
                QuoteModel.quote_id
                == quote_id
            )
        )

        if model is None:
            return None

        return self._to_domain(
            model
        )

    @staticmethod
    def _to_model(
        quote: Quote
    ) -> QuoteModel:

        calculation = (
            quote.calculation_result
        )

        model = QuoteModel(
            quote_number=(
                quote.quote_number
            ),
            modality=quote.modality,
            axle_count=quote.axle_count,
            include_return_trip=(
                quote.include_return_trip
            ),
            origin=quote.origin,
            destination=quote.destination,
            distance=quote.distance,
            valor_nota=(
                calculation.valor_nota
            ),
            geral=calculation.geral,
            pedagio=calculation.pedagio,
            custo=calculation.custo,
            subtotal=calculation.subtotal,
            total=calculation.total
        )

        if quote.issued_at is not None:
            model.issued_at = (
                quote.issued_at
            )

        model.taxes = [
            QuoteTaxModel(
                position=position,
                name=tax.nome,
                rate=tax.aliquota,
                calculation_base=(
                    tax.base_calculo
                ),
                value=tax.valor
            )
            for position, tax
            in enumerate(
                calculation.impostos,
                start=1
            )
        ]

        return model

    @staticmethod
    def _to_domain(
        model: QuoteModel
    ) -> Quote:

        taxes = tuple(
            CalculatedTax(
                nome=tax.name,
                aliquota=tax.rate,
                base_calculo=(
                    tax.calculation_base
                ),
                valor=tax.value
            )
            for tax in model.taxes
        )

        calculation = QuoteCalculationResult(
            valor_nota=model.valor_nota,
            geral=model.geral,
            pedagio=model.pedagio,
            custo=model.custo,
            subtotal=model.subtotal,
            impostos=taxes,
            total=model.total
        )

        return Quote(
            quote_id=model.quote_id,
            quote_number=model.quote_number,
            issued_at=model.issued_at,
            modality=model.modality,
            axle_count=model.axle_count,
            include_return_trip=(
                model.include_return_trip
            ),
            origin=model.origin,
            destination=model.destination,
            distance=model.distance,
            calculation_result=calculation
        )