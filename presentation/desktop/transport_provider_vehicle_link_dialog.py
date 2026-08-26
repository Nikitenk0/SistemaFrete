from tkinter import messagebox, ttk

import customtkinter as ctk

from domain.models.vehicle import VehicleStatus
from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.transport_provider_catalog_formatting import (
    VEHICLE_RELATION_OPTIONS,
)
from presentation.desktop.vehicle_catalog_formatting import (
    format_vehicle_plate,
    vehicle_type_label,
)


class TransportProviderVehicleLinkDialog:

    def __init__(
        self,
        parent,
        provider_name: str,
        search_vehicles_callback,
    ):
        self.result = None
        self._search_vehicles_callback = search_vehicles_callback
        self._vehicles_by_id = {}
        self._is_loading = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title("Vincular veículo")
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._cancel)

        self._task_runner = TkAsyncTaskRunner(
            scheduler=self._window
        )

        frame = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=16,
        )

        ctk.CTkLabel(
            frame,
            text=f"Prestador: {provider_name}",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        search = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        search.pack(fill="x", pady=(0, 8))

        self.query_entry = ctk.CTkEntry(
            search,
            placeholder_text="Placa ou tipo",
        )
        self.query_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
        )
        self.query_entry.bind(
            "<Return>",
            lambda _event: self._search(),
        )

        self.search_button = ctk.CTkButton(
            search,
            text="Pesquisar",
            width=100,
            command=self._search,
        )
        self.search_button.pack(side="left")

        self.status_label = ctk.CTkLabel(
            frame,
            text="",
        )
        self.status_label.pack(anchor="w", pady=(0, 6))

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.pack(fill="both", expand=True)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("vehicle_id", "plate", "type")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        headings = {
            "vehicle_id": "ID",
            "plate": "Placa",
            "type": "Tipo",
        }
        widths = {
            "vehicle_id": 60,
            "plate": 140,
            "type": 280,
        }
        for column in columns:
            self.tree.heading(
                column,
                text=headings[column],
            )
            self.tree.column(
                column,
                width=widths[column],
                anchor="center",
            )

        scrollbar = ttk.Scrollbar(
            tree_frame,
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

        relation_frame = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        relation_frame.pack(fill="x", pady=(10, 8))

        ctk.CTkLabel(
            relation_frame,
            text="Relação",
        ).pack(side="left", padx=(0, 8))

        self.relation_combo = ctk.CTkComboBox(
            relation_frame,
            values=list(VEHICLE_RELATION_OPTIONS),
            state="readonly",
            width=180,
        )
        self.relation_combo.pack(side="left")
        self.relation_combo.set(
            list(VEHICLE_RELATION_OPTIONS)[0]
        )

        buttons = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        buttons.pack(fill="x")

        ctk.CTkButton(
            buttons,
            text="Cancelar",
            width=95,
            command=self._cancel,
        ).pack(side="right")

        self.confirm_button = ctk.CTkButton(
            buttons,
            text="Vincular",
            width=100,
            state="disabled",
            command=self._confirm,
        )
        self.confirm_button.pack(
            side="right",
            padx=(0, 8),
        )

        self._window.geometry("720x500")
        self.query_entry.focus_set()
        self._search()
        self._window.wait_window()

    def _search(self) -> None:
        if self._is_loading:
            return

        self._set_loading(True)
        query = self.query_entry.get().strip()
        self._task_runner.run(
            task=lambda: self._search_vehicles_callback(
                query=query,
                status=VehicleStatus.ACTIVE,
                vehicle_type=None,
                limit=200,
            ),
            on_success=self._show_results,
            on_error=self._show_error,
        )

    def _show_results(self, items) -> None:
        self._vehicles_by_id = {
            item.vehicle_id: item
            for item in items
            if item.vehicle_id is not None
        }
        self.tree.delete(*self.tree.get_children())

        for item in items:
            if item.vehicle_id is None:
                continue
            self.tree.insert(
                "",
                "end",
                iid=str(item.vehicle_id),
                values=(
                    item.vehicle_id,
                    format_vehicle_plate(item.plate),
                    vehicle_type_label(
                        item.vehicle_type
                    ),
                ),
            )

        self.status_label.configure(
            text=(
                f"{len(self._vehicles_by_id)} "
                "veículo(s) ativo(s)"
            )
        )
        self._set_loading(False)

    def _show_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar veículos.\n\n"
            f"{error}",
            parent=self._window,
        )

    def _confirm(self) -> None:
        selection = self.tree.selection()
        if not selection or self._is_loading:
            return

        vehicle = self._vehicles_by_id.get(
            int(selection[0])
        )
        if vehicle is None:
            return

        try:
            relation = VEHICLE_RELATION_OPTIONS[
                self.relation_combo.get()
            ]
        except KeyError:
            return

        self.result = (vehicle, relation)
        self._window.destroy()

    def _cancel(self) -> None:
        if self._is_loading:
            return
        self.result = None
        self._window.destroy()

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
            self.confirm_button.configure(
                state="disabled"
            )
        else:
            self._on_selection()

    def _on_selection(self, _event=None) -> None:
        self.confirm_button.configure(
            state=(
                "normal"
                if (
                    self.tree.selection()
                    and not self._is_loading
                )
                else "disabled"
            )
        )
