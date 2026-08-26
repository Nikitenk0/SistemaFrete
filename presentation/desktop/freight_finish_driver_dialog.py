from decimal import Decimal
from tkinter import messagebox

import customtkinter as ctk

from presentation.desktop.freight_driver_amount_inputs import (
    parse_actual_driver_amount,
)


class FreightFinishDriverDialog:

    def __init__(
        self,
        parent,
        driver_name: str,
    ):
        self.result: Decimal | None = None

        self._window = ctk.CTkToplevel(parent)
        self._window.title("Encerrar motorista")
        self._window.transient(
            parent.winfo_toplevel()
        )
        self._window.grab_set()
        self._window.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

        frame = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        frame.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=18,
        )

        ctk.CTkLabel(
            frame,
            text="Encerrar participação do motorista",
            font=("Arial", 16, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 6),
        )

        ctk.CTkLabel(
            frame,
            text=driver_name,
        ).pack(
            anchor="w",
            pady=(0, 14),
        )

        ctk.CTkLabel(
            frame,
            text="Valor realizado do motorista",
        ).pack(
            anchor="w",
            pady=(0, 4),
        )

        self._amount_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Ex.: 2.300,00",
            width=260,
        )
        self._amount_entry.pack(
            fill="x",
            pady=(0, 16),
        )
        self._amount_entry.bind(
            "<Return>",
            lambda _event: self._confirm(),
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

        ctk.CTkButton(
            buttons,
            text="Continuar",
            width=105,
            command=self._confirm,
        ).pack(
            side="right",
            padx=(0, 8),
        )

        self._window.geometry("430x250")
        self._window.resizable(False, False)

        self._amount_entry.focus_set()
        self._window.wait_window()

    def _confirm(self) -> None:
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

        self.result = amount
        self._window.destroy()

    def _cancel(self) -> None:
        self.result = None
        self._window.destroy()
