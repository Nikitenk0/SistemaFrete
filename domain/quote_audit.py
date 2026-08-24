from dataclasses import replace

from domain.models.quote import (
    Quote,
    QuoteStatus
)
from domain.models.quote_event import (
    QuoteEvent,
    QuoteEventType
)
from domain.models.quote_version import (
    QuoteVersion
)
from domain.quote_lifecycle import (
    can_transition_quote
)


_STATUS_BY_EVENT_TYPE = {
    QuoteEventType.CALCULATED: QuoteStatus.CALCULATED,
    QuoteEventType.OFFERED: QuoteStatus.OFFERED,
    QuoteEventType.NEGOTIATION_STARTED: (
        QuoteStatus.NEGOTIATION
    ),
    QuoteEventType.APPROVED: QuoteStatus.APPROVED,
    QuoteEventType.REJECTED: QuoteStatus.REJECTED,
    QuoteEventType.CANCELLED: QuoteStatus.CANCELLED,
}


def validate_persisted_quote_version_update(
    persisted: QuoteVersion,
    proposed: QuoteVersion
) -> None:

    _validate_version_identity(
        persisted,
        proposed
    )

    if persisted.offered_price is None:
        return

    persisted_snapshot = replace(
        persisted,
        contracted_price=None,
        contracted_margin_value=None,
        contracted_margin_rate=None
    )

    proposed_snapshot = replace(
        proposed,
        contracted_price=None,
        contracted_margin_value=None,
        contracted_margin_rate=None
    )

    if persisted_snapshot != proposed_snapshot:
        raise ValueError(
            "Versão ofertada não pode ser alterada. "
            "Crie uma nova versão do orçamento."
        )

    if persisted.contracted_price is None:
        _validate_first_contracting(
            proposed
        )
        return

    if (
        persisted.contracted_price
        != proposed.contracted_price
        or persisted.contracted_margin_value
        != proposed.contracted_margin_value
        or persisted.contracted_margin_rate
        != proposed.contracted_margin_rate
    ):
        raise ValueError(
            "Versão aprovada não pode ter dados "
            "contratados alterados"
        )


def validate_quote_audit_consistency(
    quote: Quote
) -> None:

    if not quote.events:
        raise ValueError(
            "Orçamento persistido precisa possuir "
            "histórico de eventos"
        )

    version_ids = {
        version.quote_version_id
        for version in quote.versions
        if version.quote_version_id is not None
    }

    persisted_event_ids: set[int] = set()
    running_status: QuoteStatus | None = None
    last_event: QuoteEvent | None = None
    created_seen = False

    for event in quote.events:

        if event.quote_event_id is not None:
            if event.quote_event_id in persisted_event_ids:
                raise ValueError(
                    "Histórico possui evento duplicado"
                )

            persisted_event_ids.add(
                event.quote_event_id
            )

        if (
            event.quote_version_id is not None
            and event.quote_version_id not in version_ids
        ):
            raise ValueError(
                "Evento referencia versão que não pertence "
                "ao orçamento"
            )

        _validate_event_time_order(
            last_event,
            event
        )

        if event.event_type == QuoteEventType.CREATED:
            if created_seen or running_status is not None:
                raise ValueError(
                    "Evento CREATED deve iniciar o histórico"
                )

            if (
                event.previous_status is not None
                or event.new_status != QuoteStatus.DRAFT
            ):
                raise ValueError(
                    "Evento CREATED possui transição inválida"
                )

            created_seen = True
            running_status = QuoteStatus.DRAFT
            last_event = event
            continue

        if not created_seen:
            raise ValueError(
                "Histórico precisa iniciar com CREATED"
            )

        if event.event_type == QuoteEventType.PRICE_CHANGED:
            _validate_price_changed_event(
                event
            )
            last_event = event
            continue

        expected_status = _STATUS_BY_EVENT_TYPE.get(
            event.event_type
        )

        if expected_status is None:
            raise ValueError(
                "Tipo de evento não suportado no histórico"
            )

        if (
            event.previous_status is None
            or event.new_status is None
        ):
            raise ValueError(
                "Evento de mudança de estado precisa informar "
                "os status anterior e novo"
            )

        if event.previous_status != running_status:
            raise ValueError(
                "Histórico possui quebra na sequência "
                "de status"
            )

        if event.new_status != expected_status:
            raise ValueError(
                "Evento não corresponde ao status informado"
            )

        if event.new_status == running_status:
            if not (
                event.event_type == QuoteEventType.CALCULATED
                and running_status == QuoteStatus.CALCULATED
            ):
                raise ValueError(
                    "Repetição de status inválida no histórico"
                )
        elif not can_transition_quote(
            running_status,
            event.new_status
        ):
            raise ValueError(
                "Histórico possui transição de status inválida"
            )

        running_status = event.new_status
        last_event = event

    if not created_seen:
        raise ValueError(
            "Histórico precisa possuir evento CREATED"
        )

    if running_status != quote.current_status:
        raise ValueError(
            "Status atual diverge do histórico do orçamento"
        )

    _validate_offer_events(
        quote
    )

    _validate_approval_event(
        quote
    )


def _validate_version_identity(
    persisted: QuoteVersion,
    proposed: QuoteVersion
) -> None:

    identity_fields = (
        "quote_version_id",
        "quote_id",
        "version_number",
        "created_at",
        "created_by"
    )

    for field_name in identity_fields:
        if (
            getattr(persisted, field_name)
            != getattr(proposed, field_name)
        ):
            raise ValueError(
                "Identidade da versão persistida "
                "não pode ser alterada"
            )


def _validate_first_contracting(
    version: QuoteVersion
) -> None:

    if version.contracted_price is None:
        if (
            version.contracted_margin_value is not None
            or version.contracted_margin_rate is not None
        ):
            raise ValueError(
                "Margem contratada exige preço contratado"
            )
        return

    if version.contracted_margin_value is None:
        raise ValueError(
            "Preço contratado exige margem contratada"
        )

    if (
        version.bp02 not in (None, 0)
        and version.contracted_margin_rate is None
    ):
        raise ValueError(
            "Preço contratado exige taxa de margem contratada"
        )


def _validate_event_time_order(
    previous: QuoteEvent | None,
    current: QuoteEvent
) -> None:

    if (
        previous is None
        or previous.occurred_at is None
        or current.occurred_at is None
    ):
        return

    if current.occurred_at < previous.occurred_at:
        raise ValueError(
            "Eventos do orçamento estão fora de ordem temporal"
        )


def _validate_price_changed_event(
    event: QuoteEvent
) -> None:

    if (
        event.previous_status is not None
        or event.new_status is not None
    ):
        raise ValueError(
            "PRICE_CHANGED não altera status do orçamento"
        )

    if (
        event.previous_amount is None
        or event.new_amount is None
    ):
        raise ValueError(
            "PRICE_CHANGED precisa registrar os dois valores"
        )

    if not (
        event.observation
        and event.observation.strip()
    ):
        raise ValueError(
            "PRICE_CHANGED precisa possuir justificativa"
        )


def _validate_offer_events(
    quote: Quote
) -> None:

    offered_events_by_version: dict[
        int,
        QuoteEvent
    ] = {}

    for event in quote.events:
        if (
            event.event_type == QuoteEventType.OFFERED
            and event.quote_version_id is not None
        ):
            if event.quote_version_id in offered_events_by_version:
                raise ValueError(
                    "Versão do orçamento possui mais de uma oferta"
                )

            offered_events_by_version[
                event.quote_version_id
            ] = event

    for version in quote.versions:
        if version.offered_price is None:
            continue

        if version.quote_version_id is None:
            raise ValueError(
                "Versão ofertada precisa estar persistida"
            )

        event = offered_events_by_version.get(
            version.quote_version_id
        )

        if event is None:
            raise ValueError(
                "Versão ofertada não possui evento OFFERED"
            )

        if event.new_amount != version.offered_price:
            raise ValueError(
                "Preço ofertado diverge do histórico"
            )


def _validate_approval_event(
    quote: Quote
) -> None:

    approved_events = [
        event
        for event in quote.events
        if event.event_type == QuoteEventType.APPROVED
    ]

    if quote.current_status != QuoteStatus.APPROVED:
        if approved_events:
            raise ValueError(
                "Orçamento não aprovado possui evento APPROVED"
            )
        return

    if len(approved_events) != 1:
        raise ValueError(
            "Orçamento aprovado precisa possuir um único "
            "evento APPROVED"
        )

    approved_event = approved_events[0]

    if (
        approved_event.quote_version_id
        != quote.approved_version_id
    ):
        raise ValueError(
            "Evento APPROVED aponta para versão incorreta"
        )

    approved_version = next(
        version
        for version in quote.versions
        if version.quote_version_id
        == quote.approved_version_id
    )

    if (
        approved_event.new_amount
        != approved_version.contracted_price
    ):
        raise ValueError(
            "Preço contratado diverge do evento APPROVED"
        )
