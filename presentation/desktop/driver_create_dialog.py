from tkinter import messagebox

import customtkinter as ctk

from domain.models.driver import Driver
from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.driver_form import DriverForm


class DriverCreateDialog:

    def __init__(
        self,
        parent,
        create_driver_callback,
        *,
        initial_name: str = "",
        initial_cpf: str = "",
        lock_cpf: bool = False,
    ):
        self.result: Driver | None = None
        self._create_driver_callback = create_driver_callback
        self._is_saving = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title("Cadastrar motorista")
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
            include_status=False,
        )
        self.form.frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(16, 8),
        )
        self.form.prefill_identity(
            name=initial_name,
            cpf=initial_cpf,
            lock_cpf=lock_cpf,
        )

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
            text="Cadastrar",
            width=110,
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
            data = self.form.parse()
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
            text="Cadastrando motorista..."
        )

        self._task_runner.run(
            task=lambda: self._create_driver_callback(
                name=data.name,
                cpf=data.cpf,
                rg=data.rg,
                birth_date=data.birth_date,
                cnh_number=data.cnh_number,
                cnh_category=data.cnh_category,
                cnh_expiration_date=data.cnh_expiration_date,
                contacts=data.contacts,
                addresses=data.addresses,
                bank_accounts=data.bank_accounts,
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
            f"Motorista {driver.name} cadastrado com sucesso.",
            parent=self._window,
        )
        self._window.destroy()

    def _on_error(self, error: Exception) -> None:
        if not self._exists():
            return

        self._is_saving = False
        self.save_button.configure(
            state="normal",
            text="Cadastrar",
        )
        self.status_label.configure(text="")
        messagebox.showerror(
            "Erro",
            "Não foi possível cadastrar o motorista.\n\n"
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
