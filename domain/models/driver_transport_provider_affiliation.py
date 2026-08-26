from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DriverTransportProviderRole(StrEnum):
    OWNER = "OWNER"
    EMPLOYEE = "EMPLOYEE"
    CONTRACTOR = "CONTRACTOR"


@dataclass(frozen=True)
class DriverTransportProviderAffiliation:
    driver_id: int
    transport_provider_id: int
    role: DriverTransportProviderRole
    started_at: datetime

    ended_at: datetime | None = None

    driver_transport_provider_affiliation_id: int | None = None

    created_at: datetime | None = None
    created_by: int | None = None

    updated_at: datetime | None = None
    updated_by: int | None = None

    def __post_init__(self) -> None:
        if self.driver_id < 1:
            raise ValueError(
                "driver_id inválido"
            )

        if self.transport_provider_id < 1:
            raise ValueError(
                "transport_provider_id inválido"
            )

        try:
            role = DriverTransportProviderRole(
                self.role
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "role inválido"
            ) from error

        if (
            self.ended_at is not None
            and self.ended_at < self.started_at
        ):
            raise ValueError(
                "ended_at não pode ser anterior a started_at"
            )

        self._validate_optional_id(
            self.driver_transport_provider_affiliation_id,
            "driver_transport_provider_affiliation_id",
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
            "role",
            role,
        )

    @property
    def is_active(self) -> bool:
        return self.ended_at is None

    @staticmethod
    def _validate_optional_id(
        value: int | None,
        field_name: str,
    ) -> None:
        if value is not None and value < 1:
            raise ValueError(
                f"{field_name} inválido"
            )
