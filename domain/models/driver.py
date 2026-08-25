from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum

from domain.models.driver_address import (
    DriverAddress
)
from domain.models.driver_bank_account import (
    DriverBankAccount
)
from domain.models.driver_contact import (
    DriverContact
)


class DriverStatus(StrEnum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass(frozen=True)
class Driver:

    name: str
    cpf: str
    rg: str
    birth_date: date

    cnh_number: str
    cnh_category: str
    cnh_expiration_date: date

    status: DriverStatus = DriverStatus.ACTIVE

    contacts: tuple[DriverContact, ...] = ()
    addresses: tuple[DriverAddress, ...] = ()
    bank_accounts: tuple[DriverBankAccount, ...] = ()

    driver_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        name = self._required_text(
            self.name,
            "name"
        )

        cpf = "".join(
            character
            for character in self.cpf
            if character.isdigit()
        )

        if len(cpf) != 11:
            raise ValueError(
                "CPF inválido"
            )

        rg = self._required_text(
            self.rg,
            "rg"
        )

        cnh_number = self._required_text(
            self.cnh_number,
            "cnh_number"
        )

        cnh_category = self._required_text(
            self.cnh_category,
            "cnh_category"
        ).upper()

        if len(cnh_category) > 5:
            raise ValueError(
                "cnh_category inválida"
            )

        if self.birth_date > date.today():
            raise ValueError(
                "birth_date não pode estar no futuro"
            )

        if self.cnh_expiration_date <= self.birth_date:
            raise ValueError(
                "cnh_expiration_date inválida"
            )

        if not self.contacts:
            raise ValueError(
                "Motorista precisa possuir pelo menos um contato"
            )

        if not self.addresses:
            raise ValueError(
                "Motorista precisa possuir pelo menos um endereço"
            )

        if not self.bank_accounts:
            raise ValueError(
                "Motorista precisa possuir pelo menos uma conta bancária"
            )

        self._validate_single_primary(
            self.contacts,
            "contato"
        )
        self._validate_single_primary(
            self.addresses,
            "endereço"
        )
        self._validate_single_primary(
            self.bank_accounts,
            "conta bancária"
        )

        self._validate_optional_id(
            self.driver_id,
            "driver_id"
        )
        self._validate_optional_id(
            self.created_by,
            "created_by"
        )
        self._validate_optional_id(
            self.updated_by,
            "updated_by"
        )

        object.__setattr__(
            self,
            "name",
            name
        )
        object.__setattr__(
            self,
            "cpf",
            cpf
        )
        object.__setattr__(
            self,
            "rg",
            rg
        )
        object.__setattr__(
            self,
            "cnh_number",
            cnh_number
        )
        object.__setattr__(
            self,
            "cnh_category",
            cnh_category
        )

    @staticmethod
    def _required_text(
        value: str,
        field_name: str
    ) -> str:

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                f"{field_name} é obrigatório"
            )

        return cleaned

    @staticmethod
    def _validate_single_primary(
        items: tuple,
        item_name: str
    ) -> None:

        primary_count = sum(
            1
            for item in items
            if item.is_primary
        )

        if primary_count != 1:
            raise ValueError(
                f"Motorista precisa possuir exatamente um {item_name} principal"
            )

    @staticmethod
    def _validate_optional_id(
        value: int | None,
        field_name: str
    ) -> None:

        if value is not None and value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )
