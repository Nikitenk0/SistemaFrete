from dataclasses import dataclass
from decimal import Decimal
from tkinter import messagebox, ttk

import customtkinter as ctk

from domain.models.transport_provider import (
    TransportProviderStatus,
)
from presentation.desktop.async_task_runner import (
    TkAsyncTaskRunner,
)
from presentation.desktop.freight_driver_amount_inputs import (
    parse_actual_driver_amount,
)
from presentation.desktop.transport_provider_catalog_formatting import (
    driver_role_label,
    format_cpf,
    format_tax_document,
    provider_type_label,
    vehicle_relation_label,
)
from presentation.desktop.vehicle_catalog_formatting import (
    format_vehicle_plate,
    vehicle_type_label,
)


@dataclass(frozen=True)
class FreightOperationalReplacementSelection:
    transport_provider_id: int
    driver_id: int
    vehicle_id: int
    actual_transport_amount: Decimal
    provider_name: str
    driver_name: str
    vehicle_plate: str


class FreightOperationalAssignmentReplaceDialog:

    def __init__(
        self,
        parent,
        unit_position: int,
        current_context,
        search_transport_providers_callback,
        get_transport_provider_details_callback,
    ):
        self.result: (
            FreightOperationalReplacementSelection | None
        ) = None
        self._current_context = current_context
        self._search_providers_callback = (
            search_transport_providers_callback
        )
        self._get_provider_details_callback = (
            get_transport_provider_details_callback
        )
        self._providers_by_id = {}
        self._drivers_by_id = {}
        self._vehicles_by_id = {}
        self._provider_details = None
        self._is_loading = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title(
            f"Trocar conjunto operacional - Unidade {unit_position}"
        )
        self._window.transient(
            parent.winfo_toplevel()
        )
        self._window.grab_set()
        self._window.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

        self._task_runner = TkAsyncTaskRunner(
            scheduler=self._window
        )

        self._build(unit_position)
        self._search_providers()
        self._window.wait_window()

    def _build(
        self,
        unit_position: int,
    ) -> None:
        self._window.grid_rowconfigure(0, weight=1)
        self._window.grid_columnconfigure(0, weight=1)

        main = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        main.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=16,
        )
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(5, weight=1)
        main.grid_rowconfigure(8, weight=1)
        main.grid_rowconfigure(11, weight=1)

        ctk.CTkLabel(
            main,
            text=(
                f"TROCAR CONJUNTO OPERACIONAL - "
                f"UNIDADE {unit_position}"
            ),
            font=("Arial", 18, "bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        ctk.CTkLabel(
            main,
            text=(
                "Atual: "
                f"{self._current_context.provider_name_snapshot} | "
                f"{self._current_context.driver_name_snapshot} | "
                f"{self._current_context.vehicle_plate_snapshot}"
            ),
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 12),
        )

        amount_frame = ctk.CTkFrame(
            main,
            fg_color="transparent",
        )
        amount_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 12),
        )
        amount_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            amount_frame,
            text="Valor realizado pelo conjunto atual",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 10),
        )

        self._amount_entry = ctk.CTkEntry(
            amount_frame,
            placeholder_text="Ex.: 2.300,00",
        )
        self._amount_entry.grid(
            row=0,
            column=1,
            sticky="ew",
        )

        provider_search = ctk.CTkFrame(
            main,
            fg_color="transparent",
        )
        provider_search.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 6),
        )
        provider_search.grid_columnconfigure(0, weight=1)

        self._provider_query = ctk.CTkEntry(
            provider_search,
            placeholder_text=(
                "Pesquisar prestador por nome, CPF ou CNPJ"
            ),
        )
        self._provider_query.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8),
        )
        self._provider_query.bind(
            "<Return>",
            lambda _event: self._search_providers(),
        )

        self._provider_search_button = ctk.CTkButton(
            provider_search,
            text="Pesquisar",
            width=100,
            command=self._search_providers,
        )
        self._provider_search_button.grid(
            row=0,
            column=1,
        )

        self._status_label = ctk.CTkLabel(
            main,
            text="",
        )
        self._status_label.grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        provider_frame = ctk.CTkFrame(main)
        provider_frame.grid(
            row=5,
            column=0,
            sticky="nsew",
        )
        provider_frame.grid_rowconfigure(0, weight=1)
        provider_frame.grid_columnconfigure(0, weight=1)

        self._provider_tree = ttk.Treeview(
            provider_frame,
            columns=("id", "name", "document", "type"),
            show="headings",
            selectmode="browse",
            height=5,
        )
        for column, label, width in (
            ("id", "ID", 55),
            ("name", "Prestador", 280),
            ("document", "CPF / CNPJ", 155),
            ("type", "Tipo", 120),
        ):
            self._provider_tree.heading(
                column,
                text=label,
            )
            self._provider_tree.column(
                column,
                width=width,
                anchor="center",
            )

        provider_scroll = ttk.Scrollbar(
            provider_frame,
            orient="vertical",
            command=self._provider_tree.yview,
        )
        self._provider_tree.configure(
            yscrollcommand=provider_scroll.set,
        )
        self._provider_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        provider_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self._provider_tree.bind(
            "<<TreeviewSelect>>",
            self._load_selected_provider,
        )

        ctk.CTkLabel(
            main,
            text="Motorista do prestador",
            font=("Arial", 13, "bold"),
        ).grid(
            row=6,
            column=0,
            sticky="w",
            pady=(12, 5),
        )

        self._driver_hint = ctk.CTkLabel(
            main,
            text="Selecione um prestador.",
        )
        self._driver_hint.grid(
            row=7,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        driver_frame = ctk.CTkFrame(main)
        driver_frame.grid(
            row=8,
            column=0,
            sticky="nsew",
        )
        driver_frame.grid_rowconfigure(0, weight=1)
        driver_frame.grid_columnconfigure(0, weight=1)

        self._driver_tree = ttk.Treeview(
            driver_frame,
            columns=("id", "name", "cpf", "role"),
            show="headings",
            selectmode="browse",
            height=4,
        )
        for column, label, width in (
            ("id", "ID", 55),
            ("name", "Motorista", 260),
            ("cpf", "CPF", 135),
            ("role", "Vínculo", 170),
        ):
            self._driver_tree.heading(
                column,
                text=label,
            )
            self._driver_tree.column(
                column,
                width=width,
                anchor="center",
            )

        driver_scroll = ttk.Scrollbar(
            driver_frame,
            orient="vertical",
            command=self._driver_tree.yview,
        )
        self._driver_tree.configure(
            yscrollcommand=driver_scroll.set,
        )
        self._driver_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        driver_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self._driver_tree.bind(
            "<<TreeviewSelect>>",
            self._on_candidate_selection,
        )

        ctk.CTkLabel(
            main,
            text="Veículo do mesmo prestador",
            font=("Arial", 13, "bold"),
        ).grid(
            row=9,
            column=0,
            sticky="w",
            pady=(12, 5),
        )

        self._vehicle_hint = ctk.CTkLabel(
            main,
            text="Selecione um prestador.",
        )
        self._vehicle_hint.grid(
            row=10,
            column=0,
            sticky="w",
            pady=(0, 4),
        )

        vehicle_frame = ctk.CTkFrame(main)
        vehicle_frame.grid(
            row=11,
            column=0,
            sticky="nsew",
        )
        vehicle_frame.grid_rowconfigure(0, weight=1)
        vehicle_frame.grid_columnconfigure(0, weight=1)

        self._vehicle_tree = ttk.Treeview(
            vehicle_frame,
            columns=("id", "plate", "type", "relation"),
            show="headings",
            selectmode="browse",
            height=4,
        )
        for column, label, width in (
            ("id", "ID", 55),
            ("plate", "Placa", 125),
            ("type", "Tipo", 230),
            ("relation", "Relação", 160),
        ):
            self._vehicle_tree.heading(
                column,
                text=label,
            )
            self._vehicle_tree.column(
                column,
                width=width,
                anchor="center",
            )

        vehicle_scroll = ttk.Scrollbar(
            vehicle_frame,
            orient="vertical",
            command=self._vehicle_tree.yview,
        )
        self._vehicle_tree.configure(
            yscrollcommand=vehicle_scroll.set,
        )
        self._vehicle_tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        vehicle_scroll.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self._vehicle_tree.bind(
            "<<TreeviewSelect>>",
            self._on_candidate_selection,
        )

        footer = ctk.CTkFrame(
            main,
            fg_color="transparent",
        )
        footer.grid(
            row=12,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )

        ctk.CTkButton(
            footer,
            text="Cancelar",
            width=95,
            command=self._cancel,
        ).pack(side="right")

        self._confirm_button = ctk.CTkButton(
            footer,
            text="Continuar",
            width=105,
            state="disabled",
            command=self._confirm,
        )
        self._confirm_button.pack(
            side="right",
            padx=(0, 8),
        )

        self._window.geometry("860x820")
        self._window.minsize(760, 700)
        self._amount_entry.focus_set()

    def _search_providers(self) -> None:
        if self._is_loading:
            return

        self._set_loading(True)
        query = self._provider_query.get().strip()

        self._task_runner.run(
            task=lambda: self._search_providers_callback(
                query=query,
                status=TransportProviderStatus.ACTIVE,
                provider_type=None,
                limit=200,
            ),
            on_success=self._show_providers,
            on_error=self._show_error,
        )

    def _show_providers(self, providers) -> None:
        self._providers_by_id = {
            provider.transport_provider_id: provider
            for provider in providers
            if provider.transport_provider_id is not None
        }

        self._provider_tree.delete(
            *self._provider_tree.get_children()
        )
        self._clear_candidates()

        for provider in providers:
            if provider.transport_provider_id is None:
                continue

            self._provider_tree.insert(
                "",
                "end",
                iid=str(provider.transport_provider_id),
                values=(
                    provider.transport_provider_id,
                    provider.trade_name or provider.legal_name,
                    format_tax_document(
                        provider.tax_document
                    ),
                    provider_type_label(
                        provider.provider_type
                    ),
                ),
            )

        self._status_label.configure(
            text=(
                f"{len(self._providers_by_id)} "
                "prestador(es) ativo(s)"
            )
        )
        self._set_loading(False)

    def _load_selected_provider(
        self,
        _event=None,
    ) -> None:
        if self._is_loading:
            return

        selection = self._provider_tree.selection()
        if not selection:
            self._clear_candidates()
            return

        provider_id = int(selection[0])
        self._set_loading(True)
        self._status_label.configure(
            text="Carregando vínculos do prestador..."
        )

        self._task_runner.run(
            task=lambda: (
                self._get_provider_details_callback(
                    provider_id
                )
            ),
            on_success=self._show_provider_details,
            on_error=self._show_error,
        )

    def _show_provider_details(
        self,
        details,
    ) -> None:
        self._provider_details = details

        self._drivers_by_id = {
            item.driver_id: item
            for item in details.drivers
        }
        self._vehicles_by_id = {
            item.vehicle_id: item
            for item in details.vehicles
        }

        self._driver_tree.delete(
            *self._driver_tree.get_children()
        )
        for item in details.drivers:
            self._driver_tree.insert(
                "",
                "end",
                iid=str(item.driver_id),
                values=(
                    item.driver_id,
                    item.name,
                    format_cpf(item.cpf),
                    driver_role_label(item.role),
                ),
            )

        self._vehicle_tree.delete(
            *self._vehicle_tree.get_children()
        )
        for item in details.vehicles:
            self._vehicle_tree.insert(
                "",
                "end",
                iid=str(item.vehicle_id),
                values=(
                    item.vehicle_id,
                    format_vehicle_plate(
                        item.plate
                    ),
                    vehicle_type_label(
                        item.vehicle_type
                    ),
                    vehicle_relation_label(
                        item.relation
                    ),
                ),
            )

        self._driver_hint.configure(
            text=(
                f"{len(details.drivers)} "
                "motorista(s) com vínculo ativo"
            )
        )
        self._vehicle_hint.configure(
            text=(
                f"{len(details.vehicles)} "
                "veículo(s) com vínculo ativo"
            )
        )

        provider = details.provider
        self._status_label.configure(
            text=(
                "Prestador selecionado: "
                f"{provider.trade_name or provider.legal_name}"
            )
        )
        self._set_loading(False)
        self._on_candidate_selection()

    def _clear_candidates(self) -> None:
        self._provider_details = None
        self._drivers_by_id = {}
        self._vehicles_by_id = {}

        self._driver_tree.delete(
            *self._driver_tree.get_children()
        )
        self._vehicle_tree.delete(
            *self._vehicle_tree.get_children()
        )

        self._driver_hint.configure(
            text="Selecione um prestador."
        )
        self._vehicle_hint.configure(
            text="Selecione um prestador."
        )
        self._on_candidate_selection()

    def _confirm(self) -> None:
        if (
            self._is_loading
            or self._provider_details is None
        ):
            return

        driver_selection = (
            self._driver_tree.selection()
        )
        vehicle_selection = (
            self._vehicle_tree.selection()
        )

        if (
            not driver_selection
            or not vehicle_selection
        ):
            return

        try:
            amount = parse_actual_driver_amount(
                self._amount_entry.get()
            )
        except ValueError as error:
            messagebox.showwarning(
                "Valor inválido",
                str(error),
                parent=self._window,
            )
            return

        driver = self._drivers_by_id.get(
            int(driver_selection[0])
        )
        vehicle = self._vehicles_by_id.get(
            int(vehicle_selection[0])
        )
        provider = self._provider_details.provider

        if driver is None or vehicle is None:
            return

        self.result = FreightOperationalReplacementSelection(
            transport_provider_id=(
                provider.transport_provider_id
            ),
            driver_id=driver.driver_id,
            vehicle_id=vehicle.vehicle_id,
            actual_transport_amount=amount,
            provider_name=(
                provider.trade_name
                or provider.legal_name
            ),
            driver_name=driver.name,
            vehicle_plate=vehicle.plate,
        )
        self._window.destroy()

    def _show_error(
        self,
        error: Exception,
    ) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Operação não realizada",
            str(error),
            parent=self._window,
        )

    def _set_loading(
        self,
        value: bool,
    ) -> None:
        self._is_loading = value
        self._provider_search_button.configure(
            state="disabled" if value else "normal",
            text=(
                "Carregando..."
                if value
                else "Pesquisar"
            ),
        )

        if value:
            self._confirm_button.configure(
                state="disabled"
            )
        else:
            self._on_candidate_selection()

    def _on_candidate_selection(
        self,
        _event=None,
    ) -> None:
        enabled = (
            not self._is_loading
            and self._provider_details is not None
            and bool(
                self._driver_tree.selection()
            )
            and bool(
                self._vehicle_tree.selection()
            )
        )
        self._confirm_button.configure(
            state="normal" if enabled else "disabled"
        )

    def _cancel(self) -> None:
        if self._is_loading:
            return

        self.result = None
        self._window.destroy()
