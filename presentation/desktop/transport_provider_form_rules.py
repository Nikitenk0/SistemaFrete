from dataclasses import dataclass

from domain.models.transport_provider import TransportProviderType


@dataclass(frozen=True)
class TransportProviderFormPresentation:
    name_label: str
    document_label: str
    show_trade_name: bool


def get_transport_provider_form_presentation(
    provider_type: TransportProviderType,
) -> TransportProviderFormPresentation:
    provider_type = TransportProviderType(provider_type)

    if provider_type == TransportProviderType.INDIVIDUAL:
        return TransportProviderFormPresentation(
            name_label="Nome completo",
            document_label="CPF",
            show_trade_name=False,
        )

    return TransportProviderFormPresentation(
        name_label="Razão social",
        document_label="CNPJ",
        show_trade_name=True,
    )
