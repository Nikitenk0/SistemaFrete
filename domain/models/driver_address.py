from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DriverAddressType(StrEnum):

    RESIDENTIAL = "RESIDENTIAL"
    OTHER = "OTHER"


@dataclass(frozen=True)
class DriverAddress:

    postal_code: str
    street: str
    number: str
    district: str
    city: str
    state: str

    complement: str | None = None

    address_type: DriverAddressType = (
        DriverAddressType.RESIDENTIAL
    )
    is_primary: bool = False

    driver_address_id: int | None = None
    driver_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(
        self
    ) -> None:

        postal_code = "".join(
            character
            for character in self.postal_code
            if character.isdigit()
        )

        if len(postal_code) != 8:
            raise ValueError(
                "postal_code inválido"
            )

        street = self._required_text(
            self.street,
            "street"
        )
        number = self._required_text(
            self.number,
            "number"
        )
        district = self._required_text(
            self.district,
            "district"
        )
        city = self._required_text(
            self.city,
            "city"
        )

        state = self._required_text(
            self.state,
            "state"
        ).upper()

        if len(state) != 2:
            raise ValueError(
                "state inválido"
            )

        complement = self._clean_optional_text(
            self.complement
        )

        self._validate_optional_id(
            self.driver_address_id,
            "driver_address_id"
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
            "postal_code",
            postal_code
        )
        object.__setattr__(
            self,
            "street",
            street
        )
        object.__setattr__(
            self,
            "number",
            number
        )
        object.__setattr__(
            self,
            "district",
            district
        )
        object.__setattr__(
            self,
            "city",
            city
        )
        object.__setattr__(
            self,
            "state",
            state
        )
        object.__setattr__(
            self,
            "complement",
            complement
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
