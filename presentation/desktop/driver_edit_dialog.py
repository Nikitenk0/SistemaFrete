from tkinter import messagebox

import customtkinter as ctk

from domain.models.driver import Driver
from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.driver_edit_inputs import (
    build_driver_update_form_data,
)
from presentation.desktop.driver_form import DriverForm


class DriverEditDialog:

    def __init__(
        self,
        parent,
        driver: Driver,
        update_driver_callback,
    ):
        self.result: Driver | None = None
        self._driver = driver
        self._update_driver_callback = update_driver_callback
        self._is_saving = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title(f"Editar motorista #{driver.driver_id}")
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._cancel)
        self._window.grid_rowconfigure(0, weight=1)
        self._window.grid_columnconfigure(0, weight=1)

        self._task_runner = TkAsyncTaskRunner(
            scheduler=self._window
        )

        self.form = DriverForm(
            self._window,
            include_status=True,
        )
        self.form.frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(16, 8),
        )
        self.form.populate(driver)

        bottom = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
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
        self._window.minsize(720, 620)
        self._window.geometry("820x720")
        self.form.focus_name()
        self._window.wait_window()

    def _save(self) -> None:
        if self._is_saving:
            return

        try:
            registration = self.form.parse()
            update_data = build_driver_update_form_data(
                self._driver,
                registration,
                self.form.status(),
            )
        except ValueError as error:
            messagebox.showwarning(
                "Dados inválidos",
                str(error),
                parent=self._window,
            )
            return

        self._is_saving = True
        self.save_button.configure(
            state="disabled",
            text="Salvando...",
        )
        self.status_label.configure(
            text="Atualizando cadastro..."
        )

        self._task_runner.run(
            task=lambda: self._update_driver_callback(
                driver_id=update_data.driver_id,
                name=update_data.name,
                cpf=update_data.cpf,
                rg=update_data.rg,
                birth_date=update_data.birth_date,
                cnh_number=update_data.cnh_number,
                cnh_category=update_data.cnh_category,
                cnh_expiration_date=(
                    update_data.cnh_expiration_date
                ),
                contacts=update_data.contacts,
                addresses=update_data.addresses,
                bank_accounts=update_data.bank_accounts,
                status=update_data.status,
            ),
            on_success=self._on_success,
            on_error=self._on_error,
        )

    def _on_success(self, driver: Driver) -> None:
        if not self._exists():
            return
        self.result = driver
        messagebox.showinfo(
            "Sucesso",
            "Cadastro do motorista atualizado com sucesso.",
            parent=self._window,
        )
        self._window.destroy()

    def _on_error(self, error: Exception) -> None:
        if not self._exists():
            return
        self._is_saving = False
        self.save_button.configure(
            state="normal",
            text="Salvar alterações",
        )
        self.status_label.configure(text="")
        messagebox.showerror(
            "Erro",
            "Não foi possível atualizar o motorista.\n\n"
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
