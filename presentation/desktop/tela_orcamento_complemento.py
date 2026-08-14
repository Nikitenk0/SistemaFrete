import customtkinter as ctk

from presentation.desktop.estilos import (
    COR_BOTAO,
    COR_FUNDO,
    FONTE_BOTAO,
)


class TelaOrcamentoComplemento:

    def __init__(
        self,
        parent,
        voltar_callback
    ):
        self.parent = parent
        self.voltar_callback = voltar_callback

        self.criar_tela()

    def criar_tela(self):

        ctk.CTkLabel(
            self.parent,
            text="COMPLEMENTO",
            font=("Arial", 22, "bold"),
            fg_color=COR_FUNDO
        ).pack(
            pady=30
        )

        ctk.CTkLabel(
            self.parent,
            text="Tela de complemento em desenvolvimento.",
            fg_color=COR_FUNDO
        ).pack(
            pady=10
        )

        ctk.CTkButton(
            self.parent,
            text="← Voltar",
            command=self.voltar_callback,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO,
            width=120
        ).pack(
            pady=30
        )