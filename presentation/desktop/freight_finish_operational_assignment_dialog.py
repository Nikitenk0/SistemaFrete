from decimal import Decimal
from tkinter import messagebox

import customtkinter as ctk

from presentation.desktop.freight_driver_amount_inputs import (
    parse_actual_driver_amount,
)


class FreightFinishOperationalAssignmentDialog:

    def __init__(
        self,
        parent,
        unit_position: int,
        current_context,
    ):
        self.result: Decimal | None = None

        self._window = ctk.CTkToplevel(parent)
        self._window.title(
            f"Encerrar conjunto operacional - Unidade {unit_position}"
        )
        self._window.transient(
            parent.winfo_toplevel()
        )
        self._window.grab_set()
        self._window.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )

        main = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        main.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=16,
        )

        ctk.CTkLabel(
            main,
            text="ENCERRAR CONJUNTO OPERACIONAL",
            font=("Arial", 17, "bold"),
        ).pack(
            anchor="w",
            pady=(0, 6),
        )

        ctk.CTkLabel(
            main,
            text=(
                f"{current_context.provider_name_snapshot} | "
                f"{current_context.driver_name_snapshot} | "
                f"{current_context.vehicle_plate_snapshot}"
            ),
            justify="left",
            anchor="w",
        ).pack(
            fill="x",
            anchor="w",
            pady=(0, 14),
        )

        ctk.CTkLabel(
            main,
            text="Valor realizado pelo conjunto",
        ).pack(
            anchor="w",
            pady=(0, 4),
        )

        self._amount_entry = ctk.CTkEntry(
            main,
            placeholder_text="Ex.: 2.300,00",
            width=260,
        )
        self._amount_entry.pack(
            fill="x",
            pady=(0, 14),
        )

        ctk.CTkLabel(
            main,
            text=(
                "Use esta opção quando este for o último conjunto "
                "operacional da unidade. Para continuar a viagem "
                "com outro motorista/veículo, use "
                '"Trocar conjunto operacional".'
            ),
            justify="left",
            anchor="w",
            wraplength=430,
        ).pack(
            fill="x",
            pady=(0, 16),
        )

        actions = ctk.CTkFrame(
            main,
            fg_color="transparent",
        )
        actions.pack(
            fill="x",
        )

        ctk.CTkButton(
            actions,
            text="Cancelar",
            width=95,
            command=self._cancel,
        ).pack(
            side="right",
        )

        ctk.CTkButton(
            actions,
            text="Continuar",
            width=105,
            command=self._confirm,
        ).pack(
            side="right",
            padx=(0, 8),
        )

        self._window.geometry("500x330")
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
