import customtkinter as ctk

from presentation.desktop.styles import (
    BUTTON_COLOR,
    BACKGROUND_COLOR,
    BUTTON_FONT,
)


class TelaOrcamentoComplemento:

    def __init__(
        self,
        parent,
        navigate_back
    ):
        self.parent = parent
        self.navigate_back = navigate_back

        self.build()

    def build(self):

        ctk.CTkLabel(
            self.parent,
            text="COMPLEMENTO",
            font=("Arial", 22, "bold"),
            fg_color=BACKGROUND_COLOR
        ).pack(
            pady=30
        )

        ctk.CTkLabel(
            self.parent,
            text="Tela de complemento em desenvolvimento.",
            fg_color=BACKGROUND_COLOR
        ).pack(
            pady=10
        )

        ctk.CTkButton(
            self.parent,
            text="← Voltar",
            command=self.navigate_back,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT,
            width=120
        ).pack(
            pady=30
        )