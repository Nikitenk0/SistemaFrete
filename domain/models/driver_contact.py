from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DriverContact:

    phone: str

    secondary_phone: str | None = None
    email: str | None = None

    is_primary: bool = False

    driver_contact_id: int | None = None
    driver_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        phone = self._normalize_phone(
            self.phone,
            "phone"
        )

        secondary_phone = None
        if self.secondary_phone is not None:
            secondary_phone = self._normalize_phone(
                self.secondary_phone,
                "secondary_phone"
            )

        email = self._clean_optional_text(
            self.email
        )

        if (
            email is not None
            and (
                "@" not in email
                or email.startswith("@")
                or email.endswith("@")
            )
        ):
            raise ValueError(
                "email inválido"
            )

        self._validate_optional_id(
            self.driver_contact_id,
            "driver_contact_id"
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
            "phone",
            phone
        )
        object.__setattr__(
            self,
            "secondary_phone",
            secondary_phone
        )
        object.__setattr__(
            self,
            "email",
            email.lower() if email else None
        )

    @staticmethod
    def _normalize_phone(
        value: str,
        field_name: str
    ) -> str:

        normalized = "".join(
            character
            for character in value
            if character.isdigit()
        )

        if len(normalized) not in {10, 11}:
            raise ValueError(
                f"{field_name} inválido"
            )

        return normalized

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
