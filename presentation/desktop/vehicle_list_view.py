from tkinter import messagebox, ttk

import customtkinter as ctk

from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.vehicle_catalog_formatting import (
    VEHICLE_STATUS_OPTIONS,
    VEHICLE_TYPE_OPTIONS,
    format_vehicle_plate,
    vehicle_status_label,
    vehicle_type_label,
)
from presentation.desktop.vehicle_create_dialog import VehicleCreateDialog
from presentation.desktop.vehicle_edit_dialog import VehicleEditDialog


class VehicleListView:

    def __init__(
        self,
        parent,
        search_vehicles_callback,
        get_vehicle_callback,
        create_vehicle_callback,
        update_vehicle_callback,
        navigate_back,
    ):
        self.parent = parent
        self._search_vehicles_callback = search_vehicles_callback
        self._get_vehicle_callback = get_vehicle_callback
        self._create_vehicle_callback = create_vehicle_callback
        self._update_vehicle_callback = update_vehicle_callback
        self._navigate_back = navigate_back
        self._is_loading = False
        self._task_runner = TkAsyncTaskRunner(scheduler=parent)

        self._build()
        self.search()

    def _build(self) -> None:
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
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
            text="VEÍCULOS",
            font=("Arial", 22, "bold"),
        ).grid(row=0, column=0, pady=(0, 4))
        ctk.CTkLabel(
            self.main_frame,
            text="Consulte, cadastre e corrija os veículos da frota cadastrada.",
            font=("Arial", 12),
        ).grid(row=1, column=0, pady=(0, 16))

        self._build_filters()
        self._build_actions()
        self._build_results()

    def _build_filters(self) -> None:
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame.grid(row=2, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(frame, text="Placa").grid(
            row=0, column=0, pady=(0, 4)
        )
        self.query_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Digite a placa",
        )
        self.query_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 8),
        )
        self.query_entry.bind("<Return>", lambda _event: self.search())

        ctk.CTkLabel(frame, text="Status").grid(
            row=0, column=1, pady=(0, 4)
        )
        self.status_combo = ctk.CTkComboBox(
            frame,
            values=list(VEHICLE_STATUS_OPTIONS),
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

        ctk.CTkLabel(frame, text="Tipo").grid(
            row=0, column=2, pady=(0, 4)
        )
        self.type_combo = ctk.CTkComboBox(
            frame,
            values=list(VEHICLE_TYPE_OPTIONS),
            state="readonly",
            width=175,
        )
        self.type_combo.grid(row=1, column=2, sticky="ew")
        self.type_combo.set("Todos")

    def _build_actions(self) -> None:
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
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
        self.search_button.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            frame,
            text="Limpar filtros",
            width=115,
            command=self.clear_filters,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            frame,
            text="Novo veículo",
            width=120,
            command=self.create_vehicle,
        ).pack(side="left", padx=(0, 8))
        self.edit_button = ctk.CTkButton(
            frame,
            text="Editar cadastro",
            width=125,
            state="disabled",
            command=self.edit_selected_vehicle,
        )
        self.edit_button.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            frame,
            text="← Voltar",
            width=100,
            command=self._navigate_back,
        ).pack(side="right")
        self.result_count_label = ctk.CTkLabel(frame, text="")
        self.result_count_label.pack(side="right", padx=12)

    def _build_results(self) -> None:
        frame = ctk.CTkFrame(self.main_frame)
        frame.grid(row=4, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        columns = ("vehicle_id", "plate", "type", "status")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        headings = {
            "vehicle_id": "ID",
            "plate": "Placa",
            "type": "Tipo",
            "status": "Status",
        }
        widths = {
            "vehicle_id": 70,
            "plate": 130,
            "type": 240,
            "status": 110,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                minwidth=60,
                anchor="center",
            )

        vertical = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.tree.xview,
        )
        self.tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self._on_selection)
        self.tree.bind(
            "<Double-1>",
            lambda _event: self.edit_selected_vehicle(),
        )

    def search(self) -> None:
        if self._is_loading:
            return
        try:
            status = VEHICLE_STATUS_OPTIONS[self.status_combo.get()]
            vehicle_type = VEHICLE_TYPE_OPTIONS[self.type_combo.get()]
        except KeyError:
            messagebox.showwarning(
                "Filtro inválido",
                "Filtro de veículo inválido.",
                parent=self.parent,
            )
            return

        self._set_loading(True)
        query = self.query_entry.get().strip()
        self._task_runner.run(
            task=lambda: self._search_vehicles_callback(
                query=query,
                status=status,
                vehicle_type=vehicle_type,
                limit=200,
            ),
            on_success=self._show_results,
            on_error=self._show_error,
        )

    def _show_results(self, items) -> None:
        self._set_loading(False)
        self.tree.delete(*self.tree.get_children())
        for item in items:
            self.tree.insert(
                "",
                "end",
                iid=str(item.vehicle_id),
                values=(
                    item.vehicle_id,
                    format_vehicle_plate(item.plate),
                    vehicle_type_label(item.vehicle_type),
                    vehicle_status_label(item.status),
                ),
            )
        self.result_count_label.configure(text=f"{len(items)} resultado(s)")
        self.edit_button.configure(state="disabled")

    def _show_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar os veículos.\n\n"
            f"{error}",
            parent=self.parent,
        )

    def clear_filters(self) -> None:
        self.query_entry.delete(0, "end")
        self.status_combo.set("Todos")
        self.type_combo.set("Todos")
        self.search()

    def create_vehicle(self) -> None:
        dialog = VehicleCreateDialog(
            parent=self.parent,
            create_vehicle_callback=self._create_vehicle_callback,
        )
        if dialog.result is not None:
            self.search()

    def edit_selected_vehicle(self) -> None:
        selection = self.tree.selection()
        if not selection or self._is_loading:
            return
        vehicle_id = int(selection[0])
        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._get_vehicle_callback(vehicle_id),
            on_success=self._open_edit_dialog,
            on_error=self._show_vehicle_load_error,
        )

    def _open_edit_dialog(self, vehicle) -> None:
        self._set_loading(False)
        dialog = VehicleEditDialog(
            parent=self.parent,
            vehicle=vehicle,
            update_vehicle_callback=self._update_vehicle_callback,
        )
        if dialog.result is not None:
            self.search()

    def _show_vehicle_load_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível abrir o cadastro do veículo.\n\n"
            f"{error}",
            parent=self.parent,
        )

    def _set_loading(self, value: bool) -> None:
        self._is_loading = value
        self.search_button.configure(
            state="disabled" if value else "normal",
            text="Pesquisando..." if value else "Pesquisar",
        )
        if value:
            self.edit_button.configure(state="disabled")
        else:
            self._on_selection()

    def _on_selection(self, _event=None) -> None:
        state = (
            "normal"
            if self.tree.selection() and not self._is_loading
            else "disabled"
        )
        self.edit_button.configure(state=state)
