from dataclasses import dataclass
from decimal import Decimal

from domain.models.quote_additional import (
    QuoteAdditional
)
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.models.quote_version import (
    QuoteVersion
)


@dataclass(frozen=True)
class QuoteRevisionData:

    modality: str | None = None

    origin: str | None = None
    destination: str | None = None

    invoice_value: Decimal | None = None

    tracking_required: bool = False

    transport_compositions: tuple[
        QuoteTransportComposition,
        ...
    ] = ()

    additionals: tuple[
        QuoteAdditional,
        ...
    ] = ()

    internal_observation: str | None = None
    proposal_observation: str | None = None

    @classmethod
    def from_version(
        cls,
        version: QuoteVersion
    ) -> "QuoteRevisionData":

        transport_compositions = tuple(
            QuoteTransportComposition(
                position=composition.position,
                axle_count=composition.axle_count,
                include_return_trip=(
                    composition.include_return_trip
                )
            )
            for composition
            in version.transport_compositions
        )

        additionals = tuple(
            QuoteAdditional(
                additional_type=(
                    additional.additional_type
                ),
                value=additional.value,
                position=additional.position,
                custom_description=(
                    additional.custom_description
                )
            )
            for additional
            in version.additionals
        )

        return cls(
            modality=version.modality,
            origin=version.origin,
            destination=version.destination,
            invoice_value=version.invoice_value,
            tracking_required=(
                version.tracking_required
            ),
            transport_compositions=(
                transport_compositions
            ),
            additionals=additionals,
            internal_observation=(
                version.internal_observation
            ),
            proposal_observation=(
                version.proposal_observation
            )
        )
