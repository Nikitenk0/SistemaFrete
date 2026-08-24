from datetime import (
    datetime,
    timezone
)
from decimal import Decimal

from application.exceptions import (
    CustomerNotFoundError,
    InvalidQuoteDataError,
    QuoteNotFoundError
)
from application.ports.customer_unit_of_work import (
    CustomerUnitOfWorkFactory
)
from application.ports.quote_unit_of_work import (
    QuoteUnitOfWorkFactory
)
from domain.models.quote import (
    Quote,
    QuoteStatus,
    QuoteType
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


class CreateQuoteDraft:

    def __init__(
        self,
        customer_unit_of_work_factory:
            CustomerUnitOfWorkFactory,
        quote_unit_of_work_factory:
            QuoteUnitOfWorkFactory
    ):
        self._customer_unit_of_work_factory = (
            customer_unit_of_work_factory
        )

        self._quote_unit_of_work_factory = (
            quote_unit_of_work_factory
        )

    def execute(
        self,
        customer_id: int,
        quote_type: QuoteType = (
            QuoteType.PRIMARY
        ),
        primary_quote_id: int | None = None,
        modality: str | None = None,
        origin: str | None = None,
        destination: str | None = None,
        invoice_value: Decimal | None = None,
        tracking_required: bool = False,
        transport_compositions: tuple[
            QuoteTransportComposition,
            ...
        ] = (),
        internal_observation: str | None = None,
        proposal_observation: str | None = None,
        created_by: int | None = None
    ) -> Quote:

        customer = self._load_customer(
            customer_id
        )

        now = datetime.now(
            timezone.utc
        )

        with (
            self._quote_unit_of_work_factory.create()
            as unit_of_work
        ):

            primary_quote = None

            if (
                quote_type
                == QuoteType.COMPLEMENTARY
            ):

                if primary_quote_id is None:
                    raise InvalidQuoteDataError(
                        "Orçamento complementar "
                        "precisa informar o "
                        "orçamento principal"
                    )

                primary_quote = (
                    unit_of_work.quotes.get_by_id(
                        primary_quote_id
                    )
                )

                if primary_quote is None:
                    raise QuoteNotFoundError(
                        "Orçamento principal "
                        "não encontrado"
                    )

                self._validate_primary_quote(
                    primary_quote,
                    customer_id
                )

            quote_number = (
                unit_of_work.quote_numbers
                .next_number(
                    now.year
                )
            )

            try:

                version = QuoteVersion(
                    version_number=1,
                    customer_person_type_snapshot=(
                        customer.person_type
                    ),
                    customer_document_snapshot=(
                        customer.document
                    ),
                    customer_legal_name_snapshot=(
                        customer.legal_name
                    ),
                    customer_trade_name_snapshot=(
                        customer.trade_name
                    ),
                    modality=modality,
                    origin=origin,
                    destination=destination,
                    invoice_value=invoice_value,
                    tracking_required=(
                        tracking_required
                    ),
                    transport_compositions=(
                        transport_compositions
                    ),
                    internal_observation=(
                        internal_observation
                    ),
                    proposal_observation=(
                        proposal_observation
                    ),
                    created_at=now,
                    created_by=created_by
                )

                created_event = QuoteEvent(
                    event_type=(
                        QuoteEventType.CREATED
                    ),
                    new_status=(
                        QuoteStatus.DRAFT
                    ),
                    user_id=created_by,
                    occurred_at=now
                )

                quote = Quote(
                    quote_number=quote_number,
                    customer_id=customer_id,
                    quote_type=quote_type,
                    primary_quote_id=(
                        primary_quote.quote_id
                        if primary_quote is not None
                        else None
                    ),
                    freight_id=(
                        primary_quote.freight_id
                        if primary_quote is not None
                        else None
                    ),
                    current_status=(
                        QuoteStatus.DRAFT
                    ),
                    versions=(
                        version,
                    ),
                    events=(
                        created_event,
                    ),
                    created_at=now,
                    created_by=created_by
                )

            except ValueError as error:

                raise InvalidQuoteDataError(
                    str(error)
                ) from error

            created_quote = (
                unit_of_work.quotes.add(
                    quote
                )
            )

            unit_of_work.commit()

            return created_quote

    def _load_customer(
        self,
        customer_id: int
    ):

        with (
            self._customer_unit_of_work_factory.create()
            as unit_of_work
        ):

            customer = (
                unit_of_work.customers.get_by_id(
                    customer_id
                )
            )

            if customer is None:
                raise CustomerNotFoundError(
                    "Cliente não encontrado"
                )

            return customer

    @staticmethod
    def _validate_primary_quote(
        primary_quote: Quote,
        customer_id: int
    ) -> None:

        if (
            primary_quote.quote_type
            != QuoteType.PRIMARY
        ):
            raise InvalidQuoteDataError(
                "O orçamento informado não é "
                "um orçamento principal"
            )

        if (
            primary_quote.current_status
            != QuoteStatus.APPROVED
        ):
            raise InvalidQuoteDataError(
                "Complemento só pode ser criado "
                "para orçamento principal aprovado"
            )

        if (
            primary_quote.customer_id
            != customer_id
        ):
            raise InvalidQuoteDataError(
                "Complemento precisa possuir "
                "o mesmo cliente do principal"
            )
