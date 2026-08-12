import customtkinter as ctk
from telas.estilos import *

def tela_complemento(self):

    self.limpar_conteudo()

    ctk.CTkLabel(
        self.conteudo,
        text="COMPLEMENTO",
        font=("Arial", 22, "bold"),
        fg_color=COR_FUNDO
    ).pack(
        pady=30
    )

    ctk.CTkLabel(
        self.conteudo,
        text="Tela de complemento em desenvolvimento.",
        fg_color=COR_FUNDO
    ).pack(
        pady=10
    )

    ctk.CTkButton(
        self.conteudo,
        text="← Voltar",
        command=self.tela_inicial,
        fg_color=COR_BOTAO,
        text_color="white",
        font=FONTE_BOTAO,
        width=120
    ).pack(
        pady=30
    )