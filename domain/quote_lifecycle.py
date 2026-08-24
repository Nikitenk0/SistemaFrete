from domain.models.quote import (
    QuoteStatus
)


_ALLOWED_TRANSITIONS: dict[
    QuoteStatus,
    frozenset[QuoteStatus]
] = {
    QuoteStatus.DRAFT: frozenset({
        QuoteStatus.CALCULATED,
        QuoteStatus.CANCELLED
    }),
    QuoteStatus.CALCULATED: frozenset({
        QuoteStatus.OFFERED,
        QuoteStatus.CANCELLED
    }),
    QuoteStatus.OFFERED: frozenset({
        QuoteStatus.CALCULATED,
        QuoteStatus.NEGOTIATION,
        QuoteStatus.CANCELLED
    }),
    QuoteStatus.NEGOTIATION: frozenset({
        QuoteStatus.CALCULATED,
        QuoteStatus.APPROVED,
        QuoteStatus.REJECTED,
        QuoteStatus.CANCELLED
    }),
    QuoteStatus.APPROVED: frozenset(),
    QuoteStatus.REJECTED: frozenset(),
    QuoteStatus.CANCELLED: frozenset()
}


def can_transition_quote(
    current_status: QuoteStatus,
    new_status: QuoteStatus
) -> bool:

    return new_status in _ALLOWED_TRANSITIONS[
        current_status
    ]


def validate_quote_transition(
    current_status: QuoteStatus,
    new_status: QuoteStatus
) -> None:

    if not can_transition_quote(
        current_status,
        new_status
    ):
        raise ValueError(
            "Transição de status inválida: "
            f"{current_status.value} -> "
            f"{new_status.value}"
        )
