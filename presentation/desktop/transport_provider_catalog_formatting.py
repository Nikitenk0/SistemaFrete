from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProviderStatus,
    TransportProviderType,
)
from domain.models.vehicle_transport_provider_affiliation import (
    VehicleTransportProviderRelation,
)


PROVIDER_STATUS_OPTIONS = {
    "Todos": None,
    "Ativos": TransportProviderStatus.ACTIVE,
    "Inativos": TransportProviderStatus.INACTIVE,
}

PROVIDER_TYPE_OPTIONS = {
    "Todos": None,
    "Pessoa física": TransportProviderType.INDIVIDUAL,
    "Empresa": TransportProviderType.COMPANY,
}

PROVIDER_TYPE_LABELS = {
    TransportProviderType.INDIVIDUAL: "Pessoa física",
    TransportProviderType.COMPANY: "Empresa",
}

PROVIDER_STATUS_LABELS = {
    TransportProviderStatus.ACTIVE: "Ativo",
    TransportProviderStatus.INACTIVE: "Inativo",
}

DRIVER_ROLE_OPTIONS = {
    "Proprietário / sócio": DriverTransportProviderRole.OWNER,
    "Funcionário": DriverTransportProviderRole.EMPLOYEE,
    "Contratado": DriverTransportProviderRole.CONTRACTOR,
}

DRIVER_ROLE_LABELS = {
    value: label
    for label, value in DRIVER_ROLE_OPTIONS.items()
}

VEHICLE_RELATION_OPTIONS = {
    "Próprio": VehicleTransportProviderRelation.OWNED,
    "Locado": VehicleTransportProviderRelation.LEASED,
    "Contratado": VehicleTransportProviderRelation.CONTRACTED,
}

VEHICLE_RELATION_LABELS = {
    value: label
    for label, value in VEHICLE_RELATION_OPTIONS.items()
}


def provider_type_label(value: TransportProviderType) -> str:
    return PROVIDER_TYPE_LABELS[
        TransportProviderType(value)
    ]


def provider_status_label(value: TransportProviderStatus) -> str:
    return PROVIDER_STATUS_LABELS[
        TransportProviderStatus(value)
    ]


def driver_role_label(value: DriverTransportProviderRole) -> str:
    return DRIVER_ROLE_LABELS[
        DriverTransportProviderRole(value)
    ]


def vehicle_relation_label(
    value: VehicleTransportProviderRelation,
) -> str:
    return VEHICLE_RELATION_LABELS[
        VehicleTransportProviderRelation(value)
    ]


def format_tax_document(value: str) -> str:
    digits = "".join(
        character
        for character in value
        if character.isdigit()
    )
    if len(digits) == 11:
        return (
            f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-"
            f"{digits[9:]}"
        )
    if len(digits) == 14:
        return (
            f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/"
            f"{digits[8:12]}-{digits[12:]}"
        )
    return value


def format_cpf(value: str) -> str:
    digits = "".join(
        character
        for character in value
        if character.isdigit()
    )
    if len(digits) != 11:
        return value
    return (
        f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-"
        f"{digits[9:]}"
    )
