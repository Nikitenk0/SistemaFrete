from __future__ import annotations

import re

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import (
    TYPE_CHECKING
)

from domain.models.quote_version import (
    QuoteVersion
)

if TYPE_CHECKING:
    from domain.models.quote_event import (
        QuoteEvent
    )


class QuoteType(StrEnum):

    PRIMARY = "PRIMARY"
    COMPLEMENTARY = "COMPLEMENTARY"


class QuoteStatus(StrEnum):

    DRAFT = "DRAFT"
    CALCULATED = "CALCULATED"
    OFFERED = "OFFERED"
    NEGOTIATION = "NEGOTIATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Quote:

    quote_number: str
    customer_id: int

    versions: tuple[
        QuoteVersion,
        ...
    ]

    quote_type: QuoteType = (
        QuoteType.PRIMARY
    )

    current_status: QuoteStatus = (
        QuoteStatus.DRAFT
    )

    primary_quote_id: int | None = None

    freight_id: int | None = None

    approved_version_id: int | None = None

    events: tuple[
        QuoteEvent,
        ...
    ] = ()

    quote_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        if self.customer_id < 1:
            raise ValueError(
                "customer_id inválido"
            )

        if not re.fullmatch(
            r"ORC-\d{4}-\d{5,}",
            self.quote_number
        ):
            raise ValueError(
                "Número do orçamento inválido"
            )

        if not self.versions:
            raise ValueError(
                "Orçamento precisa possuir "
                "ao menos uma versão"
            )

        version_numbers = [
            version.version_number
            for version in self.versions
        ]

        if (
            len(version_numbers)
            != len(set(version_numbers))
        ):
            raise ValueError(
                "Existem versões duplicadas"
            )

        if (
            self.quote_type
            == QuoteType.PRIMARY
            and self.primary_quote_id is not None
        ):
            raise ValueError(
                "Orçamento principal não pode "
                "possuir primary_quote_id"
            )

        if (
            self.quote_type
            == QuoteType.COMPLEMENTARY
            and self.primary_quote_id is None
        ):
            raise ValueError(
                "Orçamento complementar precisa "
                "possuir primary_quote_id"
            )

        if (
            self.quote_id is not None
            and self.primary_quote_id
            == self.quote_id
        ):
            raise ValueError(
                "Orçamento não pode apontar "
                "para ele mesmo"
            )

        if (
            self.current_status
            == QuoteStatus.APPROVED
            and self.approved_version_id is None
        ):
            raise ValueError(
                "Orçamento aprovado precisa "
                "possuir versão aprovada"
            )

        if (
            self.current_status
            != QuoteStatus.APPROVED
            and self.approved_version_id is not None
        ):
            raise ValueError(
                "Versão aprovada só pode existir "
                "em orçamento aprovado"
            )

        if self.approved_version_id is not None:
            approved_versions = [
                version
                for version in self.versions
                if version.quote_version_id
                == self.approved_version_id
            ]

            if len(approved_versions) != 1:
                raise ValueError(
                    "Versão aprovada precisa pertencer "
                    "ao orçamento"
                )

            if (
                approved_versions[0].contracted_price
                is None
            ):
                raise ValueError(
                    "Versão aprovada precisa possuir "
                    "preço contratado"
                )
