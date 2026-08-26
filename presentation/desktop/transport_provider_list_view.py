from tkinter import messagebox, ttk

import customtkinter as ctk

from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.transport_provider_catalog_formatting import (
    PROVIDER_STATUS_OPTIONS,
    PROVIDER_TYPE_OPTIONS,
    format_tax_document,
    provider_status_label,
    provider_type_label,
)
from presentation.desktop.transport_provider_create_dialog import (
    TransportProviderCreateDialog,
)
from presentation.desktop.transport_provider_edit_dialog import (
    TransportProviderEditDialog,
)
from presentation.desktop.transport_provider_links_dialog import (
    TransportProviderLinksDialog,
)


class TransportProviderListView:

    def __init__(
        self,
        parent,
        search_transport_providers_callback,
        get_transport_provider_callback,
        create_transport_provider_callback,
        update_transport_provider_callback,
        get_transport_provider_details_callback,
        set_driver_transport_provider_affiliation_callback,
        set_vehicle_transport_provider_affiliation_callback,
        create_driver_callback,
        get_driver_callback,
        update_driver_callback,
        list_drivers_callback,
        search_vehicles_callback,
        navigate_back,
    ):
        self.parent = parent
        self._search_callback = search_transport_providers_callback
        self._get_callback = get_transport_provider_callback
        self._create_callback = create_transport_provider_callback
        self._update_callback = update_transport_provider_callback
        self._get_details_callback = (
            get_transport_provider_details_callback
        )
        self._set_driver_affiliation_callback = (
            set_driver_transport_provider_affiliation_callback
        )
        self._set_vehicle_affiliation_callback = (
            set_vehicle_transport_provider_affiliation_callback
        )
        self._create_driver_callback = create_driver_callback
        self._get_driver_callback = get_driver_callback
        self._update_driver_callback = update_driver_callback
        self._list_drivers_callback = list_drivers_callback
        self._search_vehicles_callback = search_vehicles_callback
        self._navigate_back = navigate_back
        self._providers_by_id = {}
        self._is_loading = False
        self._task_runner = TkAsyncTaskRunner(
            scheduler=parent
        )

        self._build()
        self.search()

    def _build(self) -> None:
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )
        self.main_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=24,
            pady=18,
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self.main_frame,
            text="PRESTADORES DE TRANSPORTE",
            font=("Arial", 22, "bold"),
        ).grid(
            row=0,
            column=0,
            pady=(0, 4),
        )

        ctk.CTkLabel(
            self.main_frame,
            text=(
                "Cadastre empresas ou transportadores e "
                "vincule seus motoristas e veículos."
            ),
            font=("Arial", 12),
        ).grid(
            row=1,
            column=0,
            pady=(0, 16),
        )

        self._build_filters()
        self._build_actions()
        self._build_results()

    def _build_filters(self) -> None:
        frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        frame.grid(
            row=2,
            column=0,
            sticky="ew",
        )
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            frame,
            text="Nome / CPF / CNPJ",
        ).grid(
            row=0,
            column=0,
            pady=(0, 4),
        )
        self.query_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Pesquisar prestador",
        )
        self.query_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 8),
        )
        self.query_entry.bind(
            "<Return>",
            lambda _event: self.search(),
        )

        ctk.CTkLabel(
            frame,
            text="Status",
        ).grid(
            row=0,
            column=1,
            pady=(0, 4),
        )
        self.status_combo = ctk.CTkComboBox(
            frame,
            values=list(PROVIDER_STATUS_OPTIONS),
            state="readonly",
            width=145,
        )
        self.status_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 8),
        )
        self.status_combo.set("Todos")

        ctk.CTkLabel(
            frame,
            text="Tipo",
        ).grid(
            row=0,
            column=2,
            pady=(0, 4),
        )
        self.type_combo = ctk.CTkComboBox(
            frame,
            values=list(PROVIDER_TYPE_OPTIONS),
            state="readonly",
            width=160,
        )
        self.type_combo.grid(
            row=1,
            column=2,
            sticky="ew",
        )
        self.type_combo.set("Todos")

    def _build_actions(self) -> None:
        frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        frame.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(14, 10),
        )

        self.search_button = ctk.CTkButton(
            frame,
            text="Pesquisar",
            width=105,
            command=self.search,
        )
        self.search_button.pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            frame,
            text="Limpar filtros",
            width=115,
            command=self.clear_filters,
        ).pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            frame,
            text="Novo prestador",
            width=125,
            command=self.create_provider,
        ).pack(
            side="left",
            padx=(0, 8),
        )

        self.edit_button = ctk.CTkButton(
            frame,
            text="Editar cadastro",
            width=125,
            state="disabled",
            command=self.edit_selected,
        )
        self.edit_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.links_button = ctk.CTkButton(
            frame,
            text="Motoristas e veículos",
            width=155,
            state="disabled",
            command=self.open_links,
        )
        self.links_button.pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            frame,
            text="← Voltar",
            width=100,
            command=self._navigate_back,
        ).pack(side="right")

        self.count_label = ctk.CTkLabel(
            frame,
            text="",
        )
        self.count_label.pack(
            side="right",
            padx=12,
        )

    def _build_results(self) -> None:
        frame = ctk.CTkFrame(self.main_frame)
        frame.grid(
            row=4,
            column=0,
            sticky="nsew",
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        columns = (
            "id",
            "name",
            "document",
            "type",
            "status",
        )
        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
        )

        for column, label, width in (
            ("id", "ID", 60),
            ("name", "Prestador", 300),
            ("document", "CPF / CNPJ", 160),
            ("type", "Tipo", 130),
            ("status", "Status", 100),
        ):
            self.tree.heading(column, text=label)
            self.tree.column(
                column,
                width=width,
                anchor="center",
            )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(
            yscrollcommand=scrollbar.set,
        )
        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self._on_selection,
        )
        self.tree.bind(
            "<Double-1>",
            lambda _event: self.open_links(),
        )

    def search(self) -> None:
        if self._is_loading:
            return

        try:
            status = PROVIDER_STATUS_OPTIONS[
                self.status_combo.get()
            ]
            provider_type = PROVIDER_TYPE_OPTIONS[
                self.type_combo.get()
            ]
        except KeyError:
            messagebox.showwarning(
                "Filtro inválido",
                "Filtro de prestador inválido.",
                parent=self.parent,
            )
            return

        self._set_loading(True)
        query = self.query_entry.get().strip()

        self._task_runner.run(
            task=lambda: self._search_callback(
                query=query,
                status=status,
                provider_type=provider_type,
                limit=200,
            ),
            on_success=self._show_results,
            on_error=self._show_error,
        )

    def _show_results(self, items) -> None:
        self._providers_by_id = {
            item.transport_provider_id: item
            for item in items
            if item.transport_provider_id is not None
        }

        self.tree.delete(
            *self.tree.get_children()
        )
        for item in items:
            if item.transport_provider_id is None:
                continue

            self.tree.insert(
                "",
                "end",
                iid=str(item.transport_provider_id),
                values=(
                    item.transport_provider_id,
                    item.trade_name or item.legal_name,
                    format_tax_document(
                        item.tax_document
                    ),
                    provider_type_label(
                        item.provider_type
                    ),
                    provider_status_label(
                        item.status
                    ),
                ),
            )

        self.count_label.configure(
            text=(
                f"{len(self._providers_by_id)} "
                "resultado(s)"
            )
        )
        self._set_loading(False)

    def _show_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar os prestadores.\n\n"
            f"{error}",
            parent=self.parent,
        )

    def clear_filters(self) -> None:
        self.query_entry.delete(0, "end")
        self.status_combo.set("Todos")
        self.type_combo.set("Todos")
        self.search()

    def create_provider(self) -> None:
        dialog = TransportProviderCreateDialog(
            parent=self.parent,
            create_transport_provider_callback=(
                self._create_callback
            ),
        )
        if dialog.result is not None:
            self.search()

    def edit_selected(self) -> None:
        provider_id = self._selected_id()
        if (
            provider_id is None
            or self._is_loading
        ):
            return

        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._get_callback(
                provider_id
            ),
            on_success=self._open_edit,
            on_error=self._show_error,
        )

    def _open_edit(self, provider) -> None:
        self._set_loading(False)
        dialog = TransportProviderEditDialog(
            parent=self.parent,
            provider=provider,
            update_transport_provider_callback=(
                self._update_callback
            ),
        )
        if dialog.result is not None:
            self.search()

    def open_links(self) -> None:
        provider_id = self._selected_id()
        if (
            provider_id is None
            or self._is_loading
        ):
            return

        TransportProviderLinksDialog(
            parent=self.parent,
            transport_provider_id=provider_id,
            get_transport_provider_details_callback=(
                self._get_details_callback
            ),
            set_driver_transport_provider_affiliation_callback=(
                self._set_driver_affiliation_callback
            ),
            set_vehicle_transport_provider_affiliation_callback=(
                self._set_vehicle_affiliation_callback
            ),
            create_driver_callback=(
                self._create_driver_callback
            ),
            get_driver_callback=(
                self._get_driver_callback
            ),
            update_driver_callback=(
                self._update_driver_callback
            ),
            list_drivers_callback=(
                self._list_drivers_callback
            ),
            search_vehicles_callback=(
                self._search_vehicles_callback
            ),
        )

    def _selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def _set_loading(self, value: bool) -> None:
        self._is_loading = value
        self.search_button.configure(
            state="disabled" if value else "normal",
            text=(
                "Pesquisando..."
                if value
                else "Pesquisar"
            ),
        )

        if value:
            self.edit_button.configure(
                state="disabled"
            )
            self.links_button.configure(
                state="disabled"
            )
        else:
            self._on_selection()

    def _on_selection(self, _event=None) -> None:
        state = (
            "normal"
            if (
                self.tree.selection()
                and not self._is_loading
            )
            else "disabled"
        )
        self.edit_button.configure(state=state)
        self.links_button.configure(state=state)
