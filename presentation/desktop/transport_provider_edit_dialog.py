from tkinter import messagebox

import customtkinter as ctk

from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.transport_provider_form import (
    TransportProviderForm,
)


class TransportProviderEditDialog:

    def __init__(
        self,
        parent,
        provider,
        update_transport_provider_callback,
    ):
        self.result = None
        self._provider = provider
        self._update_callback = update_transport_provider_callback
        self._is_saving = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title(
            f"Editar prestador #{provider.transport_provider_id}"
        )
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._cancel)

        self._task_runner = TkAsyncTaskRunner(
            scheduler=self._window
        )

        self.form = TransportProviderForm(
            self._window,
            include_status=True,
        )
        self.form.frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(18, 10),
        )
        self.form.populate(provider)

        buttons = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            padx=18,
            pady=(0, 18),
        )

        self.save_button = ctk.CTkButton(
            buttons,
            text="Salvar alterações",
            width=140,
            command=self._save,
        )
        self.save_button.pack(
            side="right",
            padx=(8, 0),
        )

        ctk.CTkButton(
            buttons,
            text="Cancelar",
            width=100,
            command=self._cancel,
        ).pack(side="right")

        self._window.geometry("620x420")
        self._window.resizable(False, False)
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

        self._set_saving(True)
        self._task_runner.run(
            task=lambda: self._update_callback(
                transport_provider_id=(
                    self._provider.transport_provider_id
                ),
                legal_name=data.legal_name,
                trade_name=data.trade_name,
                tax_document=data.tax_document,
                provider_type=data.provider_type,
                status=data.status,
            ),
            on_success=self._saved,
            on_error=self._error,
        )

    def _saved(self, provider) -> None:
        self.result = provider
        self._window.destroy()

    def _error(self, error: Exception) -> None:
        self._set_saving(False)
        messagebox.showerror(
            "Alteração não realizada",
            str(error),
            parent=self._window,
        )

    def _set_saving(self, value: bool) -> None:
        self._is_saving = value
        self.save_button.configure(
            state="disabled" if value else "normal",
            text=(
                "Salvando..."
                if value
                else "Salvar alterações"
            ),
        )

    def _cancel(self) -> None:
        if self._is_saving:
            return
        self.result = None
        self._window.destroy()
