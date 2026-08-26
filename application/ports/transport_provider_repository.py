from typing import Protocol

from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
)


class TransportProviderRepository(Protocol):

    def add(
        self,
        provider: TransportProvider,
    ) -> TransportProvider:
        ...

    def save(
        self,
        provider: TransportProvider,
    ) -> TransportProvider:
        ...

    def get_by_id(
        self,
        transport_provider_id: int,
    ) -> TransportProvider | None:
        ...

    def get_by_id_for_update(
        self,
        transport_provider_id: int,
    ) -> TransportProvider | None:
        ...

    def get_by_tax_document(
        self,
        tax_document: str,
    ) -> TransportProvider | None:
        ...

    def search(
        self,
        query: str = "",
        status: TransportProviderStatus | None = None,
        provider_type: TransportProviderType | None = None,
        limit: int = 100,
    ) -> tuple[TransportProvider, ...]:
        ...
