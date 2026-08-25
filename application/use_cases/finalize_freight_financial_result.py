from datetime import (
    datetime,
    timezone
)

from application.exceptions import (
    FreightNotFoundError,
    InvalidFreightDataError,
    InvalidFreightStateError
)
from application.ports.freight_financial_result_unit_of_work import (
    FreightFinancialResultUnitOfWorkFactory
)
from domain.freight_financial_result import (
    calculate_freight_financial_result
)
from domain.models.freight import (
    Freight,
    FreightStatus
)
from domain.models.freight_financial_result import (
    FreightFinancialResult
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
)
from domain.models.quote_version import (
    QuoteVersion
)


class FinalizeFreightFinancialResult:

    def __init__(
        self,
        unit_of_work_factory:
            FreightFinancialResultUnitOfWorkFactory
    ):
        self._unit_of_work_factory = (
            unit_of_work_factory
        )

    def execute(
        self,
        freight_id: int
    ) -> FreightFinancialResult:

        if freight_id < 1:
            raise InvalidFreightDataError(
                "freight_id inválido"
            )

        with (
            self._unit_of_work_factory.create()
            as unit_of_work
        ):

            freight = (
                unit_of_work.freights
                .get_by_id_for_update(
                    freight_id
                )
            )

            if freight is None:
                raise FreightNotFoundError(
                    "Frete não encontrado"
                )

            if (
                freight.current_status
                != FreightStatus.COMPLETED
            ):
                raise InvalidFreightStateError(
                    "Somente frete concluído pode possuir "
                    "fechamento financeiro"
                )

            existing_result = (
                unit_of_work.financial_results
                .get_by_freight_id(
                    freight_id
                )
            )

            if existing_result is not None:
                raise InvalidFreightStateError(
                    "Frete já possui fechamento financeiro"
                )

            quotes = (
                unit_of_work.quotes
                .list_by_freight_id_for_update(
                    freight_id
                )
            )

            approved_versions = (
                self._approved_quote_versions(
                    freight,
                    quotes
                )
            )

            driver_assignments = (
                unit_of_work.driver_assignments
                .list_by_freight_id(
                    freight_id
                )
            )

            expenses = (
                unit_of_work.expenses
                .list_by_freight_id(
                    freight_id
                )
            )

            try:
                financial_result = (
                    calculate_freight_financial_result(
                        freight_id=freight_id,
                        approved_quote_versions=(
                            approved_versions
                        ),
                        driver_assignments=(
                            driver_assignments
                        ),
                        expenses=expenses,
                        finalized_at=datetime.now(
                            timezone.utc
                        )
                    )
                )
            except ValueError as error:
                raise InvalidFreightDataError(
                    str(error)
                ) from error

            created_result = (
                unit_of_work.financial_results.add(
                    financial_result
                )
            )

            unit_of_work.commit()

            return created_result

    @staticmethod
    def _approved_quote_versions(
        freight: Freight,
        quotes: tuple[Quote, ...]
    ) -> tuple[QuoteVersion, ...]:

        primary_quotes = tuple(
            quote
            for quote in quotes
            if quote.quote_type == QuoteType.PRIMARY
        )

        if (
            len(primary_quotes) != 1
            or primary_quotes[0].quote_id
            != freight.primary_quote_id
        ):
            raise InvalidFreightDataError(
                "Frete precisa possuir exatamente seu "
                "orçamento principal"
            )

        primary_quote = primary_quotes[0]

        if (
            primary_quote.current_status
            != QuoteStatus.APPROVED
        ):
            raise InvalidFreightStateError(
                "Orçamento principal do frete precisa "
                "estar aprovado no fechamento financeiro"
            )

        approved_quotes = tuple(
            quote
            for quote in quotes
            if quote.current_status
            == QuoteStatus.APPROVED
        )

        versions: list[QuoteVersion] = []

        for quote in approved_quotes:
            approved_version_id = (
                quote.approved_version_id
            )

            if approved_version_id is None:
                raise InvalidFreightDataError(
                    "Orçamento aprovado não possui "
                    "approved_version_id"
                )

            matching_versions = tuple(
                version
                for version in quote.versions
                if version.quote_version_id
                == approved_version_id
            )

            if len(matching_versions) != 1:
                raise InvalidFreightDataError(
                    "Versão aprovada precisa pertencer "
                    "ao orçamento do frete"
                )

            versions.append(
                matching_versions[0]
            )

        return tuple(
            versions
        )
