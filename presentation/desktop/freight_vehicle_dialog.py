from tkinter import messagebox

import customtkinter as ctk

from domain.models.freight_vehicle_record import (
    FreightVehicleType,
)
from presentation.desktop.freight_operational_inputs import (
    VEHICLE_TYPE_OPTIONS,
    parse_vehicle_record_form,
)


class FreightVehicleDialog:

    def __init__(
        self,
        parent,
        unit_position: int,
    ):
        self.result: tuple[
            FreightVehicleType,
            str,
        ] | None = None

        self._window = ctk.CTkToplevel(parent)
        self._window.title(
            f"Registrar veículo - Unidade {unit_position}"
        )
        self._window.resizable(False, False)
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()

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
            text=f"Unidade {unit_position}",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        ctk.CTkLabel(
            frame,
            text="Tipo do veículo",
        ).pack(anchor="w")

        self._vehicle_type_combo = ctk.CTkComboBox(
            frame,
            values=list(VEHICLE_TYPE_OPTIONS),
            state="readonly",
            width=240,
        )
        self._vehicle_type_combo.pack(
            anchor="w",
            pady=(4, 12),
        )
        self._vehicle_type_combo.set(
            VEHICLE_TYPE_OPTIONS[0]
        )

        ctk.CTkLabel(
            frame,
            text="Placa",
        ).pack(anchor="w")

        self._plate_entry = ctk.CTkEntry(
            frame,
            width=180,
            placeholder_text="Ex.: ABC1D23",
        )
        self._plate_entry.pack(
            anchor="w",
            pady=(4, 16),
        )

        buttons = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        buttons.pack(fill="x")

        ctk.CTkButton(
            buttons,
            text="Cancelar",
            width=90,
            command=self._cancel,
        ).pack(side="right")

        ctk.CTkButton(
            buttons,
            text="Registrar",
            width=100,
            command=self._confirm,
        ).pack(side="right", padx=(0, 8))

        self._window.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )
        self._window.update_idletasks()

        required_width = max(
            390,
            self._window.winfo_reqwidth(),
        )
        required_height = max(
            290,
            self._window.winfo_reqheight(),
        )

        self._window.geometry(
            f"{required_width}x{required_height}"
        )

        self._plate_entry.focus_set()
        self._window.wait_window()

    def _confirm(self) -> None:
        try:
            self.result = parse_vehicle_record_form(
                self._vehicle_type_combo.get(),
                self._plate_entry.get(),
            )
        except ValueError as error:
            messagebox.showwarning(
                "Dados inválidos",
                str(error),
                parent=self._window,
            )
            return

        self._window.destroy()

    def _cancel(self) -> None:
        self.result = None
        self._window.destroy()
