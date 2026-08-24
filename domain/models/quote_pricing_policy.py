from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class AdministrativeCostPolicy:

    tracking_required: bool
    rate: Decimal
    minimum_value: Decimal

    def __post_init__(
        self
    ) -> None:

        if (
            self.rate < 0
            or self.rate >= 1
        ):
            raise ValueError(
                "Taxa administrativa inválida"
            )

        if self.minimum_value < 0:
            raise ValueError(
                "Valor mínimo administrativo "
                "não pode ser negativo"
            )


@dataclass(frozen=True)
class MarginBand:

    lower_bound_exclusive: Decimal | None
    upper_bound_inclusive: Decimal | None

    rate: Decimal

    def __post_init__(
        self
    ) -> None:

        if (
            self.rate < 0
            or self.rate >= 1
        ):
            raise ValueError(
                "Percentual de margem inválido"
            )

        if (
            self.lower_bound_exclusive is not None
            and self.lower_bound_exclusive < 0
        ):
            raise ValueError(
                "Limite inferior da margem "
                "não pode ser negativo"
            )

        if (
            self.upper_bound_inclusive is not None
            and self.upper_bound_inclusive < 0
        ):
            raise ValueError(
                "Limite superior da margem "
                "não pode ser negativo"
            )

        if (
            self.lower_bound_exclusive is not None
            and self.upper_bound_inclusive is not None
            and self.upper_bound_inclusive
            <= self.lower_bound_exclusive
        ):
            raise ValueError(
                "Faixa de margem inválida"
            )

    def contains(
        self,
        value: Decimal
    ) -> bool:

        lower_matches = (
            self.lower_bound_exclusive is None
            or value
            > self.lower_bound_exclusive
        )

        upper_matches = (
            self.upper_bound_inclusive is None
            or value
            <= self.upper_bound_inclusive
        )

        return (
            lower_matches
            and upper_matches
        )


@dataclass(frozen=True)
class QuotePricingPolicy:

    administrative_cost_policies: tuple[
        AdministrativeCostPolicy,
        ...
    ]

    margin_bands: tuple[
        MarginBand,
        ...
    ]

    tax_rate: Decimal

    def __post_init__(
        self
    ) -> None:

        if (
            self.tax_rate < 0
            or self.tax_rate >= 1
        ):
            raise ValueError(
                "Taxa de imposto inválida"
            )

        tracking_values = [
            policy.tracking_required
            for policy
            in self.administrative_cost_policies
        ]

        if (
            tracking_values.count(False) != 1
            or tracking_values.count(True) != 1
        ):
            raise ValueError(
                "Políticas administrativas "
                "devem possuir uma regra com "
                "rastreamento e uma sem "
                "rastreamento"
            )

        if not self.margin_bands:
            raise ValueError(
                "Tabela de margens não pode "
                "estar vazia"
            )

    def administrative_policy_for(
        self,
        tracking_required: bool
    ) -> AdministrativeCostPolicy:

        for policy in (
            self.administrative_cost_policies
        ):

            if (
                policy.tracking_required
                == tracking_required
            ):
                return policy

        raise ValueError(
            "Política administrativa "
            "não encontrada"
        )

    def margin_band_for(
        self,
        value: Decimal
    ) -> MarginBand:

        matching_bands = tuple(
            band
            for band in self.margin_bands
            if band.contains(
                value
            )
        )

        if len(matching_bands) != 1:
            raise ValueError(
                "Tabela de margens possui "
                "faixa ausente ou sobreposta"
            )

        return matching_bands[0]