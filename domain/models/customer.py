from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from domain.models.customer_address import (
    CustomerAddress
)
from domain.models.customer_contact import (
    CustomerContact
)
from domain.models.customer_operational_location import (
    CustomerOperationalLocation
)


class CustomerPersonType(StrEnum):

    INDIVIDUAL = "PF"
    COMPANY = "PJ"


class CustomerStatus(StrEnum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"
    RESTRICTED = "RESTRICTED"


@dataclass(frozen=True)
class Customer:

    person_type: CustomerPersonType
    document: str

    legal_name: str | None = None
    trade_name: str | None = None

    state_registration: str | None = None

    status: CustomerStatus = (
        CustomerStatus.ACTIVE
    )

    general_observation: str | None = None

    customer_group_id: int | None = None

    contacts: tuple[
        CustomerContact,
        ...
    ] = ()

    addresses: tuple[
        CustomerAddress,
        ...
    ] = ()

    operational_locations: tuple[
        CustomerOperationalLocation,
        ...
    ] = ()

    customer_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        document = "".join(
            character
            for character in self.document
            if character.isdigit()
        )

        legal_name = self._clean_optional_text(
            self.legal_name
        )

        trade_name = self._clean_optional_text(
            self.trade_name
        )

        if not legal_name and not trade_name:
            raise ValueError(
                "Nome, razão social ou nome fantasia "
                "é obrigatório"
            )

        expected_document_length = (
            11
            if self.person_type
            == CustomerPersonType.INDIVIDUAL
            else 14
        )

        if (
            len(document)
            != expected_document_length
        ):
            document_name = (
                "CPF"
                if self.person_type
                == CustomerPersonType.INDIVIDUAL
                else "CNPJ"
            )

            raise ValueError(
                f"{document_name} inválido"
            )

        primary_contacts = sum(
            1
            for contact in self.contacts
            if contact.is_primary
        )

        if primary_contacts > 1:
            raise ValueError(
                "Cliente não pode possuir mais "
                "de um contato principal"
            )

        primary_addresses = sum(
            1
            for address in self.addresses
            if address.is_primary
        )

        if primary_addresses > 1:
            raise ValueError(
                "Cliente não pode possuir mais "
                "de um endereço principal"
            )

        object.__setattr__(
            self,
            "document",
            document
        )

        object.__setattr__(
            self,
            "legal_name",
            legal_name
        )

        object.__setattr__(
            self,
            "trade_name",
            trade_name
        )

    @staticmethod
    def _clean_optional_text(
        value: str | None
    ) -> str | None:

        if value is None:
            return None

        cleaned_value = value.strip()

        return (
            cleaned_value
            if cleaned_value
            else None
        )