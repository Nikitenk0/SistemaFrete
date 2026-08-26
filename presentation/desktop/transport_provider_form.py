from dataclasses import dataclass

import customtkinter as ctk

from domain.models.transport_provider import (
    TransportProvider,
    TransportProviderStatus,
    TransportProviderType,
)
from presentation.desktop.transport_provider_catalog_formatting import (
    PROVIDER_STATUS_LABELS,
    PROVIDER_TYPE_LABELS,
    provider_status_label,
    provider_type_label,
)
from presentation.desktop.transport_provider_form_rules import (
    get_transport_provider_form_presentation,
)


@dataclass(frozen=True)
class TransportProviderFormData:
    legal_name: str
    trade_name: str | None
    tax_document: str
    provider_type: TransportProviderType
    status: TransportProviderStatus


class TransportProviderForm:

    def __init__(
        self,
        parent,
        *,
        include_status: bool,
    ):
        self._include_status = include_status

        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.frame,
            text="Dados do prestador",
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(16, 14),
        )

        ctk.CTkLabel(
            self.frame,
            text="Tipo",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(18, 10),
            pady=8,
        )

        self.type_combo = ctk.CTkComboBox(
            self.frame,
            values=list(PROVIDER_TYPE_LABELS.values()),
            state="readonly",
            command=self._on_type_changed,
        )
        self.type_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=8,
        )
        self.type_combo.set(
            PROVIDER_TYPE_LABELS[
                TransportProviderType.COMPANY
            ]
        )

        self._name_label = ctk.CTkLabel(
            self.frame,
            text="Razão social",
        )
        self._name_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=(18, 10),
            pady=8,
        )

        self._legal_name = ctk.CTkEntry(
            self.frame,
            placeholder_text=(
                "Ex.: Exemplo 123 Transportes LTDA"
            ),
        )
        self._legal_name.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=8,
        )

        self._trade_name_label = ctk.CTkLabel(
            self.frame,
            text="Nome fantasia (opcional)",
        )
        self._trade_name_label.grid(
            row=3,
            column=0,
            sticky="w",
            padx=(18, 10),
            pady=8,
        )

        self._trade_name = ctk.CTkEntry(
            self.frame,
            placeholder_text="Ex.: Exemplo 123",
        )
        self._trade_name.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=8,
        )

        self._document_label = ctk.CTkLabel(
            self.frame,
            text="CNPJ",
        )
        self._document_label.grid(
            row=4,
            column=0,
            sticky="w",
            padx=(18, 10),
            pady=8,
        )

        self._tax_document = ctk.CTkEntry(
            self.frame,
            placeholder_text="Somente números ou formatado",
        )
        self._tax_document.grid(
            row=4,
            column=1,
            sticky="ew",
            padx=(0, 18),
            pady=8,
        )

        self.status_combo = None
        if include_status:
            ctk.CTkLabel(
                self.frame,
                text="Status",
            ).grid(
                row=5,
                column=0,
                sticky="w",
                padx=(18, 10),
                pady=(8, 16),
            )
            self.status_combo = ctk.CTkComboBox(
                self.frame,
                values=list(PROVIDER_STATUS_LABELS.values()),
                state="readonly",
            )
            self.status_combo.grid(
                row=5,
                column=1,
                sticky="ew",
                padx=(0, 18),
                pady=(8, 16),
            )
            self.status_combo.set("Ativo")

        self._apply_type_presentation(
            TransportProviderType.COMPANY
        )

    def _on_type_changed(
        self,
        selected_label: str,
    ) -> None:
        try:
            provider_type = next(
                item
                for item, label in PROVIDER_TYPE_LABELS.items()
                if label == selected_label
            )
        except StopIteration:
            return

        self._apply_type_presentation(
            provider_type
        )

    def _apply_type_presentation(
        self,
        provider_type: TransportProviderType,
    ) -> None:
        presentation = (
            get_transport_provider_form_presentation(
                provider_type
            )
        )

        self._name_label.configure(
            text=presentation.name_label
        )
        self._document_label.configure(
            text=presentation.document_label
        )

        if presentation.show_trade_name:
            self._trade_name_label.grid()
            self._trade_name.grid()
        else:
            self._trade_name.delete(0, "end")
            self._trade_name_label.grid_remove()
            self._trade_name.grid_remove()

    def parse(self) -> TransportProviderFormData:
        legal_name = self._legal_name.get().strip()
        tax_document = self._tax_document.get().strip()

        try:
            provider_type = next(
                item
                for item, label in PROVIDER_TYPE_LABELS.items()
                if label == self.type_combo.get()
            )
        except StopIteration as error:
            raise ValueError(
                "Tipo de prestador inválido"
            ) from error

        presentation = (
            get_transport_provider_form_presentation(
                provider_type
            )
        )

        trade_name = (
            self._trade_name.get().strip() or None
            if presentation.show_trade_name
            else None
        )

        status = TransportProviderStatus.ACTIVE
        if self.status_combo is not None:
            try:
                status = next(
                    item
                    for item, label
                    in PROVIDER_STATUS_LABELS.items()
                    if label == self.status_combo.get()
                )
            except StopIteration as error:
                raise ValueError(
                    "Status do prestador inválido"
                ) from error

        normalized = TransportProvider(
            legal_name=legal_name,
            trade_name=trade_name,
            tax_document=tax_document,
            provider_type=provider_type,
            status=status,
        )

        return TransportProviderFormData(
            legal_name=normalized.legal_name,
            trade_name=normalized.trade_name,
            tax_document=normalized.tax_document,
            provider_type=normalized.provider_type,
            status=normalized.status,
        )

    def populate(
        self,
        provider: TransportProvider,
    ) -> None:
        self.type_combo.set(
            provider_type_label(
                provider.provider_type
            )
        )
        self._apply_type_presentation(
            provider.provider_type
        )

        self._legal_name.delete(0, "end")
        self._legal_name.insert(
            0,
            provider.legal_name,
        )

        self._trade_name.delete(0, "end")
        if (
            provider.provider_type
            == TransportProviderType.COMPANY
        ):
            self._trade_name.insert(
                0,
                provider.trade_name or "",
            )

        self._tax_document.delete(0, "end")
        self._tax_document.insert(
            0,
            provider.tax_document,
        )

        if self.status_combo is not None:
            self.status_combo.set(
                provider_status_label(
                    provider.status
                )
            )

    def focus_name(self) -> None:
        self._legal_name.focus_set()
