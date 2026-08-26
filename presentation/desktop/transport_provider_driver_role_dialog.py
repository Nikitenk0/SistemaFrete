import customtkinter as ctk

from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderRole,
)
from presentation.desktop.transport_provider_catalog_formatting import (
    DRIVER_ROLE_OPTIONS,
)


class TransportProviderDriverRoleDialog:

    def __init__(
        self,
        parent,
        driver_name: str,
    ):
        self.result: DriverTransportProviderRole | None = None

        self._window = ctk.CTkToplevel(parent)
        self._window.title("Vínculo do motorista")
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._cancel)

        frame = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=18,
        )

        ctk.CTkLabel(
            frame,
            text="Vínculo com o prestador",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            frame,
            text=driver_name,
        ).pack(anchor="w", pady=(0, 14))

        self._role_combo = ctk.CTkComboBox(
            frame,
            values=list(DRIVER_ROLE_OPTIONS),
            state="readonly",
        )
        self._role_combo.pack(fill="x", pady=(0, 16))
        self._role_combo.set(list(DRIVER_ROLE_OPTIONS)[0])

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

        self._window.geometry("430x220")
        self._window.resizable(False, False)
        self._window.wait_window()

    def _confirm(self) -> None:
        try:
            self.result = DRIVER_ROLE_OPTIONS[
                self._role_combo.get()
            ]
        except KeyError:
            return

        self._window.destroy()

    def _cancel(self) -> None:
        self.result = None
        self._window.destroy()
