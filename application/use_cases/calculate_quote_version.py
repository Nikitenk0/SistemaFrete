from dataclasses import replace
from datetime import (
    datetime,
    timezone
)
import logging

from application.exceptions import (
    InvalidQuoteDataError,
    QuoteVersionCalculationError,
    RouteNotFoundError,
    RouteSearchError
)
from application.parsers.distance_km import (
    parse_distance_km
)
from application.parsers.monetary_value import (
    parse_monetary_value
)
from application.ports.quote_pricing_policy_provider import (
    QuotePricingPolicyProvider
)
from application.ports.route_searcher import (
    RouteSearcher
)
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.pricing.quote_pricing import (
    calculate_quote_pricing
)


logger = logging.getLogger(
    "sistemafrete.application."
    "calculate_quote_version"
)


class CalculateQuoteVersion:

    def __init__(
        self,
        route_searcher: RouteSearcher,
        pricing_policy_provider:
            QuotePricingPolicyProvider
    ):
        self._route_searcher = route_searcher
        self._pricing_policy_provider = (
            pricing_policy_provider
        )

    def execute(
        self,
        version: QuoteVersion
    ) -> QuoteVersion:

        self._validate_version(
            version
        )

        calculated_compositions: list[
            QuoteTransportComposition
        ] = []

        canonical_origin = version.origin
        canonical_destination = version.destination

        assert canonical_origin is not None
        assert canonical_destination is not None

        for composition in (
            version.transport_compositions
        ):

            route_result = self._search_route(
                origin=canonical_origin,
                destination=canonical_destination,
                composition=composition
            )

            try:

                calculated_composition = replace(
                    composition,
                    distance_km=(
                        parse_distance_km(
                            route_result.distancia
                        )
                    ),
                    driver_amount=(
                        parse_monetary_value(
                            route_result.geral
                        )
                    ),
                    toll_amount=(
                        parse_monetary_value(
                            route_result.pedagio
                        )
                    )
                )

            except Exception as error:

                logger.exception(
                    "Falha ao interpretar resultado "
                    "da composição %s",
                    composition.position
                )

                raise QuoteVersionCalculationError(
                    "Não foi possível interpretar "
                    "o resultado da composição "
                    f"{composition.position}"
                ) from error

            calculated_compositions.append(
                calculated_composition
            )

            if len(calculated_compositions) == 1:
                canonical_origin = (
                    route_result.origem
                )
                canonical_destination = (
                    route_result.destino
                )

        try:

            pricing_policy = (
                self._pricing_policy_provider
                .get_effective_policy(
                    datetime.now(
                        timezone.utc
                    )
                )
            )

            pricing_result = (
                calculate_quote_pricing(
                    invoice_value=(
                        version.invoice_value
                    ),
                    transport_compositions=(
                        tuple(
                            calculated_compositions
                        )
                    ),
                    origin=canonical_origin,
                    destination=(
                        canonical_destination
                    ),
                    tracking_required=(
                        version
                        .tracking_required
                    ),
                    pricing_policy=(
                        pricing_policy
                    ),
                    additionals=(
                        version.additionals
                    )
                )
            )

        except (
            InvalidQuoteDataError,
            RouteNotFoundError,
            RouteSearchError,
            QuoteVersionCalculationError
        ):
            raise

        except Exception as error:

            logger.exception(
                "Falha técnica ao calcular "
                "versão do orçamento"
            )

            raise QuoteVersionCalculationError(
                "Não foi possível calcular "
                "a versão do orçamento"
            ) from error

        return replace(
            version,
            origin=canonical_origin,
            destination=canonical_destination,
            transport_compositions=(
                tuple(
                    calculated_compositions
                )
            ),
            driver_amount=(
                pricing_result.driver_amount
            ),
            toll_amount=(
                pricing_result.toll_amount
            ),
            additional_total=(
                pricing_result.additional_total
            ),
            insurance_components=(
                pricing_result
                .insurance_components
            ),
            freight_insurance_total=(
                pricing_result
                .freight_insurance_total
            ),
            bp01=pricing_result.bp01,
            administrative_rate=(
                pricing_result
                .administrative_rate
            ),
            administrative_minimum=(
                pricing_result
                .administrative_minimum
            ),
            administrative_cost=(
                pricing_result
                .administrative_cost
            ),
            bp02=pricing_result.bp02,
            margin_band_minimum=(
                pricing_result
                .margin_band_minimum
            ),
            margin_band_maximum=(
                pricing_result
                .margin_band_maximum
            ),
            standard_margin_rate=(
                pricing_result
                .standard_margin_rate
            ),
            standard_margin_value=(
                pricing_result
                .standard_margin_value
            ),
            target_net_value=(
                pricing_result
                .target_net_value
            ),
            tax_rate=(
                pricing_result.tax_rate
            ),
            tax_value=(
                pricing_result.tax_value
            ),
            calculated_price=(
                pricing_result
                .calculated_price
            ),
            rounded_price=(
                pricing_result.rounded_price
            )
        )

    def _search_route(
        self,
        origin: str,
        destination: str,
        composition: QuoteTransportComposition
    ):

        try:

            route_result = (
                self._route_searcher.search(
                    origin,
                    destination,
                    composition.axle_count,
                    composition.include_return_trip
                )
            )

        except Exception as error:

            logger.exception(
                "Falha técnica ao pesquisar rota "
                "da composição %s",
                composition.position
            )

            raise RouteSearchError(
                "Não foi possível pesquisar "
                "a rota da composição "
                f"{composition.position}"
            ) from error

        if route_result is None:
            raise RouteNotFoundError(
                "Nenhuma rota encontrada para "
                "a composição "
                f"{composition.position}"
            )

        return route_result

    @staticmethod
    def _validate_version(
        version: QuoteVersion
    ) -> None:

        if version.invoice_value is None:
            raise InvalidQuoteDataError(
                "Valor da nota é obrigatório"
            )

        if (
            version.origin is None
            or not version.origin.strip()
        ):
            raise InvalidQuoteDataError(
                "Origem é obrigatória"
            )

        if (
            version.destination is None
            or not version.destination.strip()
        ):
            raise InvalidQuoteDataError(
                "Destino é obrigatório"
            )

        if not version.transport_compositions:
            raise InvalidQuoteDataError(
                "Orçamento precisa possuir "
                "ao menos uma composição de transporte"
            )

        if version.offered_price is not None:
            raise InvalidQuoteDataError(
                "Versão ofertada não pode "
                "ser recalculada"
            )

        if version.contracted_price is not None:
            raise InvalidQuoteDataError(
                "Versão contratada não pode "
                "ser recalculada"
            )
