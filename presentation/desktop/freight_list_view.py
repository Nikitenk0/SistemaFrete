from datetime import datetime
from decimal import Decimal
from tkinter import messagebox, ttk

import customtkinter as ctk

from application.dtos.freight_query import (
    FreightListItem,
)
from presentation.desktop.async_task_runner import (
    TkAsyncTaskRunner,
)
from presentation.desktop.freight_list_filters import (
    STATUS_OPTIONS,
    freight_status_label,
    parse_freight_list_filters,
)


class FreightListView:

    def __init__(
        self,
        parent,
        list_freights_callback,
        open_freight_callback,
        navigate_back,
    ):
        self.parent = parent
        self._list_freights_callback = (
            list_freights_callback
        )
        self._open_freight_callback = (
            open_freight_callback
        )
        self._navigate_back = navigate_back
        self._is_loading = False
        self._local_timezone = (
            datetime.now().astimezone().tzinfo
        )
        self._task_runner = TkAsyncTaskRunner(
            scheduler=parent
        )

        self._build()
        self.search()

    def _build(self) -> None:

        self.parent.grid_rowconfigure(
            0,
            weight=1,
        )
        self.parent.grid_columnconfigure(
            0,
            weight=1,
        )

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
        self.main_frame.grid_columnconfigure(
            0,
            weight=1,
        )
        self.main_frame.grid_rowconfigure(
            4,
            weight=1,
        )

        ctk.CTkLabel(
            self.main_frame,
            text="FRETES",
            font=("Arial", 22, "bold"),
        ).grid(
            row=0,
            column=0,
            pady=(0, 4),
        )

        ctk.CTkLabel(
            self.main_frame,
            text=(
                "Consulte fretes por cliente, status "
                "e período de conclusão."
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

        filter_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        filter_frame.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        for column in range(4):
            filter_frame.grid_columnconfigure(
                column,
                weight=1,
            )

        ctk.CTkLabel(
            filter_frame,
            text="Cliente ID",
        ).grid(
            row=0,
            column=0,
            pady=(0, 4),
        )
        self.customer_id_entry = ctk.CTkEntry(
            filter_frame,
            width=130,
            placeholder_text="Ex.: 15",
        )
        self.customer_id_entry.grid(
            row=1,
            column=0,
            padx=6,
        )

        ctk.CTkLabel(
            filter_frame,
            text="Status",
        ).grid(
            row=0,
            column=1,
            pady=(0, 4),
        )
        self.status_combo = ctk.CTkComboBox(
            filter_frame,
            values=list(STATUS_OPTIONS),
            state="readonly",
            width=145,
        )
        self.status_combo.grid(
            row=1,
            column=1,
            padx=6,
        )
        self.status_combo.set(
            "Todos"
        )

        ctk.CTkLabel(
            filter_frame,
            text="Concluído de",
        ).grid(
            row=0,
            column=2,
            pady=(0, 4),
        )
        self.completed_from_entry = ctk.CTkEntry(
            filter_frame,
            width=145,
            placeholder_text="DD/MM/AAAA",
        )
        self.completed_from_entry.grid(
            row=1,
            column=2,
            padx=6,
        )

        ctk.CTkLabel(
            filter_frame,
            text="Concluído até",
        ).grid(
            row=0,
            column=3,
            pady=(0, 4),
        )
        self.completed_to_entry = ctk.CTkEntry(
            filter_frame,
            width=145,
            placeholder_text="DD/MM/AAAA",
        )
        self.completed_to_entry.grid(
            row=1,
            column=3,
            padx=6,
        )

    def _build_actions(self) -> None:

        action_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        action_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(14, 10),
        )

        self.search_button = ctk.CTkButton(
            action_frame,
            text="Pesquisar",
            width=110,
            command=self.search,
        )
        self.search_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.clear_button = ctk.CTkButton(
            action_frame,
            text="Limpar filtros",
            width=120,
            command=self.clear_filters,
        )
        self.clear_button.pack(
            side="left",
            padx=(0, 8),
        )

        self.open_button = ctk.CTkButton(
            action_frame,
            text="Abrir frete",
            width=110,
            state="disabled",
            command=self.open_selected_freight,
        )
        self.open_button.pack(
            side="left",
            padx=(0, 8),
        )

        ctk.CTkButton(
            action_frame,
            text="← Voltar",
            width=100,
            command=self._navigate_back,
        ).pack(
            side="right",
        )

        self.result_count_label = ctk.CTkLabel(
            action_frame,
            text="",
        )
        self.result_count_label.pack(
            side="right",
            padx=12,
        )

    def _build_results(self) -> None:

        table_frame = ctk.CTkFrame(
            self.main_frame,
        )
        table_frame.grid(
            row=4,
            column=0,
            sticky="nsew",
        )
        table_frame.grid_rowconfigure(
            0,
            weight=1,
        )
        table_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        columns = (
            "freight_id",
            "customer",
            "quote",
            "origin",
            "destination",
            "status",
            "revenue",
            "completed",
            "financial",
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
        )

        headings = {
            "freight_id": "Frete",
            "customer": "Cliente",
            "quote": "Orçamento",
            "origin": "Origem",
            "destination": "Destino",
            "status": "Status",
            "revenue": "Receita",
            "completed": "Conclusão",
            "financial": "Financeiro",
        }

        widths = {
            "freight_id": 65,
            "customer": 170,
            "quote": 115,
            "origin": 160,
            "destination": 160,
            "status": 105,
            "revenue": 110,
            "completed": 95,
            "financial": 90,
        }

        for column in columns:
            self.tree.heading(
                column,
                text=headings[column],
            )
            self.tree.column(
                column,
                width=widths[column],
                minwidth=60,
                anchor=(
                    "e"
                    if column == "revenue"
                    else "center"
                    if column in {
                        "freight_id",
                        "status",
                        "completed",
                        "financial",
                    }
                    else "w"
                ),
            )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=(
                vertical_scrollbar.set
            ),
            xscrollcommand=(
                horizontal_scrollbar.set
            ),
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self._on_tree_selection,
        )
        self.tree.bind(
            "<Double-1>",
            self._on_tree_double_click,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )

    def search(self) -> None:

        if self._is_loading:
            return

        try:
            filters = parse_freight_list_filters(
                customer_id_text=(
                    self.customer_id_entry.get()
                ),
                status_label=(
                    self.status_combo.get()
                ),
                completed_from_text=(
                    self.completed_from_entry.get()
                ),
                completed_to_text=(
                    self.completed_to_entry.get()
                ),
                timezone_info=(
                    self._local_timezone
                ),
            )
        except ValueError as error:
            messagebox.showwarning(
                "Filtros inválidos",
                str(error),
            )
            return

        self._set_loading(
            True
        )

        self._task_runner.run(
            task=lambda: self._list_freights_callback(
                customer_id=filters.customer_id,
                status=filters.status,
                completed_from=filters.completed_from,
                completed_to=filters.completed_to,
            ),
            on_success=self._on_search_success,
            on_error=self._on_search_error,
        )

    def clear_filters(self) -> None:

        if self._is_loading:
            return

        self.customer_id_entry.delete(
            0,
            "end",
        )
        self.completed_from_entry.delete(
            0,
            "end",
        )
        self.completed_to_entry.delete(
            0,
            "end",
        )
        self.status_combo.set(
            "Todos"
        )

        self.search()

    def _on_search_success(
        self,
        items: tuple[FreightListItem, ...],
    ) -> None:
        if not self._view_exists():
            return

        self._replace_rows(
            items
        )
        self.result_count_label.configure(
            text=(
                f"{len(items)} frete(s)"
            )
        )
        self._set_loading(
            False
        )

    def _on_search_error(
        self,
        error: Exception,
    ) -> None:
        if not self._view_exists():
            return

        self._set_loading(
            False
        )
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar os fretes.\n\n"
            f"{error}",
        )

    def _replace_rows(
        self,
        items: tuple[FreightListItem, ...],
    ) -> None:

        for item_id in self.tree.get_children():
            self.tree.delete(
                item_id
            )

        for item in items:
            self.tree.insert(
                "",
                "end",
                iid=str(item.freight_id),
                values=(
                    item.freight_id,
                    item.customer_name,
                    item.primary_quote_number,
                    item.origin,
                    item.destination,
                    freight_status_label(
                        item.current_status
                    ),
                    self._format_currency(
                        item.contracted_revenue
                    ),
                    self._format_date(
                        item.completed_at
                    ),
                    (
                        "Fechado"
                        if item.financially_closed
                        else "Aberto"
                    ),
                ),
            )

    def open_selected_freight(self) -> None:
        if self._is_loading:
            return

        selection = self.tree.selection()
        if not selection:
            return

        try:
            freight_id = int(selection[0])
        except (TypeError, ValueError):
            messagebox.showerror(
                "Erro",
                "Não foi possível identificar o frete selecionado.",
            )
            return

        self._open_freight_callback(
            freight_id
        )

    def _on_tree_selection(self, _event=None) -> None:
        if self._is_loading:
            self.open_button.configure(state="disabled")
            return

        self.open_button.configure(
            state=(
                "normal"
                if self.tree.selection()
                else "disabled"
            )
        )

    def _on_tree_double_click(self, _event=None) -> None:
        self.open_selected_freight()

    def _set_loading(
        self,
        value: bool,
    ) -> None:
        self._is_loading = value
        self.search_button.configure(
            state=(
                "disabled"
                if value
                else "normal"
            ),
            text=(
                "Consultando..."
                if value
                else "Pesquisar"
            ),
        )
        self.clear_button.configure(
            state=(
                "disabled"
                if value
                else "normal"
            )
        )
        self.open_button.configure(
            state=(
                "disabled"
                if value or not self.tree.selection()
                else "normal"
            )
        )

    def _view_exists(self) -> bool:
        try:
            return bool(
                self.main_frame.winfo_exists()
            )
        except Exception:
            return False

    @staticmethod
    def _format_date(
        value: datetime | None,
    ) -> str:
        if value is None:
            return "--"
        return value.astimezone().strftime(
            "%d/%m/%Y"
        ) if value.tzinfo is not None else value.strftime(
            "%d/%m/%Y"
        )

    @staticmethod
    def _format_currency(
        value: Decimal,
    ) -> str:
        formatted = f"{value:,.2f}"
        formatted = formatted.replace(
            ",",
            "TEMP",
        ).replace(
            ".",
            ",",
        ).replace(
            "TEMP",
            ".",
        )
        return f"R$ {formatted}"
