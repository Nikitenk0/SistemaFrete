from tkinter import messagebox, ttk

import customtkinter as ctk

from domain.models.vehicle import Vehicle
from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.vehicle_catalog_formatting import (
    format_vehicle_plate,
    vehicle_type_label,
)


class FreightVehicleDialog:

    def __init__(
        self,
        parent,
        unit_position: int,
        search_vehicles_callback,
    ):
        self.result: Vehicle | None = None
        self._search_vehicles_callback = search_vehicles_callback
        self._vehicles_by_id: dict[int, Vehicle] = {}
        self._is_loading = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title(f"Selecionar veículo - Unidade {unit_position}")
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._cancel)
        self._window.grid_rowconfigure(0, weight=1)
        self._window.grid_columnconfigure(0, weight=1)
        self._task_runner = TkAsyncTaskRunner(scheduler=self._window)

        frame = ctk.CTkFrame(self._window, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=22, pady=18)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            frame,
            text=f"Unidade {unit_position}",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        ctk.CTkLabel(
            frame,
            text="Somente veículos ativos e livres são exibidos.",
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        search_frame = ctk.CTkFrame(frame, fg_color="transparent")
        search_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)

        self._query_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Placa ou tipo do veículo",
        )
        self._query_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._query_entry.bind("<Return>", lambda _event: self._search())
        self._search_button = ctk.CTkButton(
            search_frame,
            text="Pesquisar",
            width=100,
            command=self._search,
        )
        self._search_button.grid(row=0, column=1)

        self._status_label = ctk.CTkLabel(frame, text="", anchor="w")
        self._status_label.grid(row=3, column=0, sticky="ew", pady=(0, 6))

        results_frame = ctk.CTkFrame(frame)
        results_frame.grid(row=4, column=0, sticky="nsew")
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        columns = ("vehicle_id", "plate", "vehicle_type")
        self._tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("vehicle_id", text="ID")
        self._tree.heading("plate", text="Placa")
        self._tree.heading("vehicle_type", text="Tipo")
        self._tree.column("vehicle_id", width=65, minwidth=55, anchor="center")
        self._tree.column("plate", width=130, minwidth=110, anchor="center")
        self._tree.column("vehicle_type", width=250, minwidth=180, anchor="w")

        vertical = ttk.Scrollbar(
            results_frame, orient="vertical", command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=vertical.set)
        self._tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        self._tree.bind("<<TreeviewSelect>>", self._on_selection)
        self._tree.bind("<Double-1>", lambda _event: self._confirm())

        ctk.CTkLabel(
            frame,
            text=(
                "Cadastros novos ou correções devem ser feitos "
                "em Cadastros > Veículos."
            ),
            anchor="w",
        ).grid(row=5, column=0, sticky="ew", pady=(10, 8))

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.grid(row=6, column=0, sticky="ew")
        buttons.grid_columnconfigure(0, weight=1)
        self._select_button = ctk.CTkButton(
            buttons,
            text="Selecionar",
            width=105,
            state="disabled",
            command=self._confirm,
        )
        self._select_button.grid(row=0, column=1, padx=(8, 8))
        ctk.CTkButton(
            buttons,
            text="Cancelar",
            width=95,
            command=self._cancel,
        ).grid(row=0, column=2)

        self._window.update_idletasks()
        self._window.minsize(620, 430)
        self._window.geometry("700x520")
        self._query_entry.focus_set()
        self._search()
        self._window.wait_window()

    def _search(self) -> None:
        if self._is_loading:
            return
        self._set_loading(True)
        query = self._query_entry.get().strip()
        self._task_runner.run(
            task=lambda: self._search_vehicles_callback(
                query=query,
                limit=200,
            ),
            on_success=self._show_results,
            on_error=self._show_error,
        )

    def _show_results(self, vehicles: tuple[Vehicle, ...]) -> None:
        if not self._exists():
            return
        self._vehicles_by_id = {
            vehicle.vehicle_id: vehicle
            for vehicle in vehicles
            if vehicle.vehicle_id is not None
        }
        self._tree.delete(*self._tree.get_children())
        for vehicle in vehicles:
            if vehicle.vehicle_id is None:
                continue
            self._tree.insert(
                "",
                "end",
                iid=str(vehicle.vehicle_id),
                values=(
                    vehicle.vehicle_id,
                    format_vehicle_plate(vehicle.plate),
                    vehicle_type_label(vehicle.vehicle_type),
                ),
            )
        self._status_label.configure(
            text=f"{len(self._vehicles_by_id)} veículo(s) disponível(is)"
        )
        self._set_loading(False)

    def _show_error(self, error: Exception) -> None:
        if not self._exists():
            return
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar os veículos disponíveis.\n\n"
            f"{error}",
            parent=self._window,
        )

    def _confirm(self) -> None:
        if self._is_loading:
            return
        selection = self._tree.selection()
        if not selection:
            return
        vehicle = self._vehicles_by_id.get(int(selection[0]))
        if vehicle is None:
            return
        self.result = vehicle
        self._window.destroy()

    def _cancel(self) -> None:
        if self._is_loading:
            return
        self.result = None
        if self._exists():
            self._window.destroy()

    def _set_loading(self, value: bool) -> None:
        self._is_loading = value
        if not self._exists():
            return
        self._search_button.configure(
            state="disabled" if value else "normal",
            text="Pesquisando..." if value else "Pesquisar",
        )
        if value:
            self._select_button.configure(state="disabled")
            self._status_label.configure(
                text="Consultando veículos disponíveis..."
            )
        else:
            self._on_selection()

    def _on_selection(self, _event=None) -> None:
        if not self._exists():
            return
        self._select_button.configure(
            state=(
                "normal"
                if self._tree.selection() and not self._is_loading
                else "disabled"
            )
        )

    def _exists(self) -> bool:
        try:
            return bool(self._window.winfo_exists())
        except Exception:
            return False
