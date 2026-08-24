from dataclasses import replace
from datetime import (
    datetime,
    timezone
)

from application.dtos.quote_revision_data import (
    QuoteRevisionData
)
from application.exceptions import (
    InvalidQuoteDataError,
    InvalidQuoteStateError,
    QuoteConcurrentModificationError,
    QuoteNotFoundError
)
from application.ports.quote_unit_of_work import (
    QuoteUnitOfWorkFactory
)
from application.ports.quote_version_calculator import (
    QuoteVersionCalculator
)
from domain.models.quote import (
    Quote,
    QuoteStatus
)
from domain.models.quote_additional import (
    QuoteAdditional
)
from domain.models.quote_event import (
    QuoteEvent,
    QuoteEventType
)
from domain.models.quote_transport_composition import (
    QuoteTransportComposition
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.quote_lifecycle import (
    validate_quote_transition
)


class ReviseQuote:

    def __init__(
        self,
        quote_unit_of_work_factory:
            QuoteUnitOfWorkFactory,
        quote_version_calculator:
            QuoteVersionCalculator
    ):
        self._quote_unit_of_work_factory = (
            quote_unit_of_work_factory
        )
        self._quote_version_calculator = (
            quote_version_calculator
        )

    def execute(
        self,
        quote_id: int,
        reason: str,
        revision_data: QuoteRevisionData | None = None,
        user_id: int | None = None
    ) -> Quote:

        cleaned_reason = reason.strip()

        if not cleaned_reason:
            raise InvalidQuoteDataError(
                "Revisão do orçamento exige justificativa"
            )

        original_quote = self._load_quote(
            quote_id
        )

        self._validate_can_revise(
            original_quote
        )

        source_version = self._latest_version(
            original_quote
        )

        data = (
            revision_data
            if revision_data is not None
            else QuoteRevisionData.from_version(
                source_version
            )
        )

        now = datetime.now(
            timezone.utc
        )

        draft_version = self._build_revision(
            source_version=source_version,
            data=data,
            now=now,
            user_id=user_id
        )

        calculated_version = (
            self._quote_version_calculator.execute(
                draft_version
            )
        )

        with (
            self._quote_unit_of_work_factory.create()
            as unit_of_work
        ):

            current_quote = (
                unit_of_work.quotes
                .get_by_id_for_update(
                    quote_id
                )
            )

            if current_quote is None:
                raise QuoteNotFoundError(
                    "Orçamento não encontrado"
                )

            if current_quote != original_quote:
                raise QuoteConcurrentModificationError(
                    "O orçamento foi alterado durante "
                    "a revisão. Recarregue os dados "
                    "e tente novamente."
                )

            current_version = self._latest_version(
                current_quote
            )

            if (
                current_version.quote_version_id
                != source_version.quote_version_id
                or current_version.version_number
                != source_version.version_number
            ):
                raise QuoteConcurrentModificationError(
                    "A versão atual do orçamento mudou "
                    "durante a revisão"
                )

            first_update = replace(
                current_quote,
                current_status=(
                    QuoteStatus.CALCULATED
                ),
                versions=(
                    *current_quote.versions,
                    calculated_version
                )
            )

            saved_with_version = (
                unit_of_work.quotes.save(
                    first_update
                )
            )

            persisted_version = next(
                (
                    version
                    for version
                    in saved_with_version.versions
                    if version.version_number
                    == calculated_version.version_number
                ),
                None
            )

            if (
                persisted_version is None
                or persisted_version.quote_version_id
                is None
            ):
                raise InvalidQuoteDataError(
                    "Nova versão do orçamento não pôde "
                    "ser identificada após persistência"
                )

            calculated_event = QuoteEvent(
                event_type=(
                    QuoteEventType.CALCULATED
                ),
                quote_version_id=(
                    persisted_version.quote_version_id
                ),
                previous_status=(
                    original_quote.current_status
                ),
                new_status=(
                    QuoteStatus.CALCULATED
                ),
                observation=cleaned_reason,
                user_id=user_id,
                occurred_at=now
            )

            final_quote = replace(
                saved_with_version,
                events=(
                    *saved_with_version.events,
                    calculated_event
                )
            )

            saved_quote = (
                unit_of_work.quotes.save(
                    final_quote
                )
            )

            unit_of_work.commit()

            return saved_quote

    def _load_quote(
        self,
        quote_id: int
    ) -> Quote:

        with (
            self._quote_unit_of_work_factory.create()
            as unit_of_work
        ):

            quote = (
                unit_of_work.quotes.get_by_id(
                    quote_id
                )
            )

            if quote is None:
                raise QuoteNotFoundError(
                    "Orçamento não encontrado"
                )

            return quote

    @staticmethod
    def _validate_can_revise(
        quote: Quote
    ) -> None:

        if quote.current_status not in (
            QuoteStatus.OFFERED,
            QuoteStatus.NEGOTIATION
        ):
            raise InvalidQuoteStateError(
                "Nova versão só pode ser criada "
                "depois que o orçamento foi ofertado"
            )

        try:
            validate_quote_transition(
                quote.current_status,
                QuoteStatus.CALCULATED
            )
        except ValueError as error:
            raise InvalidQuoteStateError(
                str(error)
            ) from error

    @classmethod
    def _build_revision(
        cls,
        source_version: QuoteVersion,
        data: QuoteRevisionData,
        now: datetime,
        user_id: int | None
    ) -> QuoteVersion:

        compositions = tuple(
            QuoteTransportComposition(
                position=composition.position,
                axle_count=composition.axle_count,
                include_return_trip=(
                    composition.include_return_trip
                )
            )
            for composition
            in data.transport_compositions
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
            in data.additionals
        )

        try:
            return QuoteVersion(
                version_number=(
                    source_version.version_number
                    + 1
                ),
                customer_person_type_snapshot=(
                    source_version
                    .customer_person_type_snapshot
                ),
                customer_document_snapshot=(
                    source_version
                    .customer_document_snapshot
                ),
                customer_legal_name_snapshot=(
                    source_version
                    .customer_legal_name_snapshot
                ),
                customer_trade_name_snapshot=(
                    source_version
                    .customer_trade_name_snapshot
                ),
                modality=data.modality,
                origin=data.origin,
                destination=data.destination,
                invoice_value=data.invoice_value,
                tracking_required=(
                    data.tracking_required
                ),
                transport_compositions=(
                    compositions
                ),
                additionals=additionals,
                internal_observation=(
                    data.internal_observation
                ),
                proposal_observation=(
                    data.proposal_observation
                ),
                created_at=now,
                created_by=user_id
            )
        except ValueError as error:
            raise InvalidQuoteDataError(
                str(error)
            ) from error

    @staticmethod
    def _latest_version(
        quote: Quote
    ) -> QuoteVersion:

        return max(
            quote.versions,
            key=lambda version: (
                version.version_number
            )
        )
