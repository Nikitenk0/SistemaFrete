from tkinter import messagebox

import customtkinter as ctk

from domain.models.vehicle import Vehicle
from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.vehicle_form import VehicleForm


class VehicleEditDialog:

    def __init__(self, parent, vehicle: Vehicle, update_vehicle_callback):
        self.result: Vehicle | None = None
        self._vehicle = vehicle
        self._update_vehicle_callback = update_vehicle_callback
        self._is_saving = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title(f"Editar veículo #{vehicle.vehicle_id}")
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._cancel)
        self._window.grid_rowconfigure(0, weight=1)
        self._window.grid_columnconfigure(0, weight=1)

        self._task_runner = TkAsyncTaskRunner(scheduler=self._window)
        self.form = VehicleForm(self._window, include_status=True)
        self.form.frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(16, 8),
        )
        self.form.populate(vehicle)

        bottom = ctk.CTkFrame(self._window, fg_color="transparent")
        bottom.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 16),
        )
        bottom.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(bottom, text="")
        self.status_label.grid(row=0, column=0, sticky="w")

        self.save_button = ctk.CTkButton(
            bottom,
            text="Salvar alterações",
            width=140,
            command=self._save,
        )
        self.save_button.grid(row=0, column=1, padx=(8, 8))
        ctk.CTkButton(
            bottom,
            text="Cancelar",
            width=100,
            command=self._cancel,
        ).grid(row=0, column=2)

        self._window.update_idletasks()
        self._window.minsize(480, 330)
        self._window.geometry("560x390")
        self.form.focus_plate()
        self._window.wait_window()

    def _save(self) -> None:
        if self._is_saving:
            return
        try:
            data = self.form.parse()
        except ValueError as error:
            messagebox.showwarning(
                "Dados inválidos",
                str(error),
                parent=self._window,
            )
            return

        self._is_saving = True
        self.save_button.configure(state="disabled", text="Salvando...")
        self.status_label.configure(text="Atualizando cadastro...")
        self._task_runner.run(
            task=lambda: self._update_vehicle_callback(
                vehicle_id=self._vehicle.vehicle_id,
                plate=data.plate,
                vehicle_type=data.vehicle_type,
                status=data.status,
            ),
            on_success=self._on_success,
            on_error=self._on_error,
        )

    def _on_success(self, vehicle: Vehicle) -> None:
        if not self._exists():
            return
        self.result = vehicle
        messagebox.showinfo(
            "Sucesso",
            "Cadastro do veículo atualizado com sucesso.",
            parent=self._window,
        )
        self._window.destroy()

    def _on_error(self, error: Exception) -> None:
        if not self._exists():
            return
        self._is_saving = False
        self.save_button.configure(state="normal", text="Salvar alterações")
        self.status_label.configure(text="")
        messagebox.showerror(
            "Erro",
            "Não foi possível atualizar o veículo.\n\n"
            f"{error}",
            parent=self._window,
        )

    def _cancel(self) -> None:
        if self._is_saving:
            return
        if self._exists():
            self._window.destroy()

    def _exists(self) -> bool:
        try:
            return bool(self._window.winfo_exists())
        except Exception:
            return False
