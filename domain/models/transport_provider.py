from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TransportProviderType(StrEnum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class TransportProviderStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


def normalize_transport_provider_document(
    value: str,
) -> str:
    document = "".join(
        character
        for character in value
        if character.isdigit()
    )

    if len(document) not in {11, 14}:
        raise ValueError(
            "tax_document inválido"
        )

    return document


@dataclass(frozen=True)
class TransportProvider:
    legal_name: str
    tax_document: str
    provider_type: TransportProviderType

    trade_name: str | None = None
    status: TransportProviderStatus = (
        TransportProviderStatus.ACTIVE
    )

    transport_provider_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(self) -> None:
        legal_name = self.legal_name.strip()

        if not legal_name:
            raise ValueError(
                "legal_name é obrigatório"
            )

        trade_name = (
            self.trade_name.strip()
            if self.trade_name is not None
            else None
        )
        if trade_name == "":
            trade_name = None

        try:
            provider_type = TransportProviderType(
                self.provider_type
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "provider_type inválido"
            ) from error

        try:
            status = TransportProviderStatus(
                self.status
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "status inválido"
            ) from error

        tax_document = (
            normalize_transport_provider_document(
                self.tax_document
            )
        )

        expected_length = (
            11
            if provider_type
            == TransportProviderType.INDIVIDUAL
            else 14
        )
        if len(tax_document) != expected_length:
            raise ValueError(
                "tax_document incompatível com provider_type"
            )

        self._validate_optional_id(
            self.transport_provider_id,
            "transport_provider_id",
        )
        self._validate_optional_id(
            self.created_by,
            "created_by",
        )
        self._validate_optional_id(
            self.updated_by,
            "updated_by",
        )

        object.__setattr__(
            self,
            "legal_name",
            legal_name,
        )
        object.__setattr__(
            self,
            "trade_name",
            trade_name,
        )
        object.__setattr__(
            self,
            "tax_document",
            tax_document,
        )
        object.__setattr__(
            self,
            "provider_type",
            provider_type,
        )
        object.__setattr__(
            self,
            "status",
            status,
        )

    @staticmethod
    def _validate_optional_id(
        value: int | None,
        field_name: str,
    ) -> None:
        if value is not None and value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )
