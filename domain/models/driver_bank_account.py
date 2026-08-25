from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DriverBankAccountType(StrEnum):

    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"
    PAYMENT = "PAYMENT"


class DriverPixKeyType(StrEnum):

    CPF = "CPF"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    RANDOM = "RANDOM"


@dataclass(frozen=True)
class DriverBankAccount:

    bank_code: str
    agency: str
    account: str
    account_type: DriverBankAccountType

    account_digit: str | None = None

    pix_key_type: DriverPixKeyType | None = None
    pix_key: str | None = None

    is_primary: bool = False

    driver_bank_account_id: int | None = None
    driver_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        bank_code = "".join(
            character
            for character in self.bank_code
            if character.isdigit()
        )

        if len(bank_code) != 3:
            raise ValueError(
                "bank_code inválido"
            )

        agency = self._required_text(
            self.agency,
            "agency"
        )
        account = self._required_text(
            self.account,
            "account"
        )

        account_digit = self._clean_optional_text(
            self.account_digit
        )
        pix_key = self._clean_optional_text(
            self.pix_key
        )

        if (
            self.pix_key_type is None
            and pix_key is not None
        ):
            raise ValueError(
                "pix_key_type é obrigatório quando pix_key é informado"
            )

        if (
            self.pix_key_type is not None
            and pix_key is None
        ):
            raise ValueError(
                "pix_key é obrigatório quando pix_key_type é informado"
            )

        self._validate_optional_id(
            self.driver_bank_account_id,
            "driver_bank_account_id"
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
            "bank_code",
            bank_code
        )
        object.__setattr__(
            self,
            "agency",
            agency
        )
        object.__setattr__(
            self,
            "account",
            account
        )
        object.__setattr__(
            self,
            "account_digit",
            account_digit
        )
        object.__setattr__(
            self,
            "pix_key",
            pix_key
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
    def _clean_optional_text(
        value: str | None
    ) -> str | None:

        if value is None:
            return None

        cleaned = value.strip()

        return cleaned if cleaned else None

    @staticmethod
    def _validate_optional_id(
        value: int | None,
        field_name: str
    ) -> None:

        if value is not None and value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )
