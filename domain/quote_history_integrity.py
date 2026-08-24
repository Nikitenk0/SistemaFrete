from dataclasses import replace

from domain.models.quote import (
    QuoteStatus
)
from domain.models.quote_event import (
    QuoteEvent
)
from domain.models.quote_version import (
    QuoteVersion
)


_TERMINAL_STATUSES = frozenset({
    QuoteStatus.APPROVED,
    QuoteStatus.REJECTED,
    QuoteStatus.CANCELLED
})


def validate_persisted_quote_state_update(
    persisted_status: QuoteStatus,
    persisted_approved_version_id: int | None,
    candidate_status: QuoteStatus,
    candidate_approved_version_id: int | None
) -> None:

    if (
        persisted_status in _TERMINAL_STATUSES
        and candidate_status != persisted_status
    ):
        raise ValueError(
            "Status terminal do orçamento não pode ser alterado"
        )

    if (
        persisted_approved_version_id is not None
        and candidate_approved_version_id
        != persisted_approved_version_id
    ):
        raise ValueError(
            "Versão aprovada do orçamento não pode ser alterada"
        )


def validate_persisted_version_update(
    persisted: QuoteVersion,
    candidate: QuoteVersion
) -> None:

    if (
        persisted.quote_version_id
        != candidate.quote_version_id
    ):
        raise ValueError(
            "Identidade da versão do orçamento não pode ser alterada"
        )

    if persisted.offered_price is None:
        return

    if persisted.contracted_price is None:

        normalized_candidate = replace(
            candidate,
            contracted_price=(
                persisted.contracted_price
            ),
            contracted_margin_value=(
                persisted.contracted_margin_value
            ),
            contracted_margin_rate=(
                persisted.contracted_margin_rate
            )
        )

        if normalized_candidate != persisted:
            raise ValueError(
                "Versão ofertada do orçamento não pode ser alterada"
            )

        contracted_values = (
            candidate.contracted_price,
            candidate.contracted_margin_value,
            candidate.contracted_margin_rate
        )

        if any(
            value is not None
            for value in contracted_values
        ) and not all(
            value is not None
            for value in contracted_values
        ):
            raise ValueError(
                "Dados contratados da versão precisam ser definidos juntos"
            )

        return

    if candidate != persisted:
        raise ValueError(
            "Versão aprovada do orçamento não pode ser alterada"
        )


def validate_persisted_event_unchanged(
    persisted: QuoteEvent,
    candidate: QuoteEvent
) -> None:

    if persisted != candidate:
        raise ValueError(
            "Evento persistido do orçamento não pode ser alterado"
        )
