import customtkinter as ctk
from tkinter import *

from estilos import *

from services.qualp import QualP

class MenuPrincipal:

    def __init__(self, master):

        self.master = master

        self.master.title("Sistema")
        self.master.geometry(f"{LARGURA_JANELA}x{ALTURA_JANELA}")
        self.master.configure(fg_color=COR_FUNDO)

        # ==========================
        # MENU
        # ==========================

        self.menu = ctk.CTkFrame(
            master,
            fg_color=COR_MENU,
            width=LARGURA_MENU
        )

        self.menu.pack(side=LEFT, fill=Y)
        self.menu.pack_propagate(False)

        # ==========================
        # CONTEÚDO
        # ==========================

        self.conteudo = ctk.CTkFrame(
            master,
            fg_color=COR_FUNDO
        )

        self.conteudo.pack(
            side=RIGHT,
            expand=True,
            fill=BOTH
        )
        # ==========================
        # BOTÕES DO MENU
        # ==========================
        ctk.CTkButton(
            self.menu,
            text="Orçamento",
            command=self.tela_orcamento,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO
        ).pack(fill=X, pady=5, padx=10)

        ctk.CTkButton(
            self.menu,
            text="Documentos",
            command=self.tela_documentos,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO
        ).pack(fill=X, pady=5, padx=10)

        self.tela_inicial()

    # ====================================

    def limpar_conteudo(self):
        """Remove todos os componentes da área principal."""
        for widget in self.conteudo.winfo_children():
            widget.destroy()

    # ====================================

    def tela_inicial(self):

        self.limpar_conteudo()

        ctk.CTkLabel(
            self.conteudo,
            text="Sistema",
            font=FONTE_TITULO,
            fg_color=COR_FUNDO
        ).pack(pady=50)

    # ====================================

    def tela_orcamento(self):

        self.limpar_conteudo()

        ctk.CTkLabel(
            self.conteudo,
            text="ORÇAMENTO",
            font=("Arial",22,"bold"),
            fg_color=COR_FUNDO
        ).pack(pady=30)

        ctk.CTkLabel(
            self.conteudo,
            text="Aqui ficarão os campos do orçamento.",
            fg_color=COR_FUNDO
        ).pack()

        ctk.CTkLabel(
            self.conteudo,
            text="Origem",
            fg_color=COR_FUNDO
        ).pack()

        self.txt_origem = ctk.CTkEntry(
            self.conteudo,
            width=400
        )

        self.txt_origem.pack(pady=5)

        ctk.CTkLabel(
            self.conteudo,
            text="Destino",
            fg_color=COR_FUNDO
        ).pack()

        self.txt_destino = ctk.CTkEntry(
            self.conteudo,
            width=400
        )

        self.txt_destino.pack(pady=5)

        # Quantidade de eixos
        ctk.CTkLabel(
            self.conteudo,
            text="Quantidade de eixos",
            fg_color=COR_FUNDO
        ).pack()

        self.txt_eixos = ctk.CTkComboBox(
            self.conteudo,
            values=[str(i) for i in range(2, 13)],
            width=100
        )

        self.txt_eixos.pack(pady=5)

        self.txt_eixos.set("6")

        # ====================================
        # Calcular Volta
        # ====================================
        self.var_calcular_volta = ctk.BooleanVar(value=False)

        self.switch_volta = ctk.CTkSwitch(
            self.conteudo,
            text="Calcular Volta",
            variable=self.var_calcular_volta
        )

        self.switch_volta.pack(pady=10)


        ctk.CTkButton(
            self.conteudo,
            text="Pesquisar",
            command=self.pesquisar_orcamento
        ).pack(pady=20)

        # ==========================
        # Resultado da pesquisa
        # ==========================

        ctk.CTkLabel(
            self.conteudo,
            text="Distância"
        ).pack()

        self.lbl_distancia = ctk.CTkLabel(
            self.conteudo,
            text="--"
        )

        self.lbl_distancia.pack(pady=(0, 10))

        
        ctk.CTkButton(
            self.conteudo,
            text="← Voltar",
            command=self.tela_inicial,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO,
            width=120
        ).pack(pady=30)
    # ====================================

    def tela_documentos(self):

        self.limpar_conteudo()

        ctk.CTkLabel(
            self.conteudo,
            text="DOCUMENTOS",
            font=("Arial",22,"bold"),
            fg_color=COR_FUNDO
        ).pack(pady=30)

        ctk.CTkLabel(
            self.conteudo,
            text="Aqui ficarão os documentos.",
            fg_color=COR_FUNDO
        ).pack()

        ctk.CTkButton(
            self.conteudo,
            text="← Voltar",
            command=self.tela_inicial,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO,
            width=15
        ).pack(pady=30)

    def pesquisar_orcamento(self):

        origem = self.txt_origem.get()
        destino = self.txt_destino.get()
        eixos = int(self.txt_eixos.get())
        calcular_volta = self.var_calcular_volta.get()

        robo = QualP()

        resultado = robo.pesquisar(
            origem,
            destino,
            eixos,
            calcular_volta
        )

        self.lbl_distancia.configure(
            text=resultado["distancia"]
        )

        print(resultado)

