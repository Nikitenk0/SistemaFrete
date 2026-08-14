import customtkinter as ctk

from tkinter import LEFT, RIGHT, BOTH, Y, X

from presentation.desktop.estilos import *
from presentation.desktop.tela_orcamento_fechada import TelaOrcamentoFechada
from presentation.desktop.tela_documentos import TelaDocumentos
from presentation.desktop.tela_orcamento_complemento import TelaOrcamentoComplemento



class MenuPrincipal:

    def __init__(
        self,
        master,
        orcamento_callback,
        pdf_callback
    ):
        self.master = master
        self.orcamento_callback = orcamento_callback
        self.pdf_callback = pdf_callback

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

        # ==========================
        # BOTÃO ORÇAMENTO
        # ==========================


        self.btn_orcamento = ctk.CTkButton(
            self.menu,
            text="Orçamento",
            command=self.mostrar_submenu_orcamento,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO
        )

        self.btn_orcamento.pack(
            fill=X,
            pady=5,
            padx=10
        )



        # ==========================
        # SUBMENU ORÇAMENTO
        # ==========================

        self.submenu_orcamento = ctk.CTkFrame(
            self.master,
            fg_color=COR_MENU,
            width=220    
        )
        self.submenu_orcamento.pack_propagate(
            False
        )

        ctk.CTkButton(
            self.submenu_orcamento,
            text="1 - Carga Fechada",
            command=self.tela_orcamento,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )

        ctk.CTkButton(
            self.submenu_orcamento,
            text="2 - Complemento",
            command=self.tela_complemento,
            fg_color=COR_BOTAO,
            text_color="white",
            font=FONTE_BOTAO
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )
                
        # ==========================
        # BOTÃO DOCUMENTOS
        # ==========================


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

    def mostrar_submenu_orcamento(self):

        if self.submenu_orcamento.winfo_ismapped():

            self.submenu_orcamento.pack_forget()

        else:

            self.submenu_orcamento.place(
                x=LARGURA_MENU,
                y=0
            )


    def tela_orcamento(self):

        # Fecha o submenu
        self.submenu_orcamento.place_forget()

        self.limpar_conteudo()

        self.tela_orcamento_atual = TelaOrcamentoFechada(
            self.conteudo,
            orcamento_callback=self.orcamento_callback,
            pdf_callback=self.pdf_callback,
            voltar_callback=self.tela_inicial
        )

    def tela_complemento(self):

        self.submenu_orcamento.place_forget()

        self.limpar_conteudo()

        self.tela_complemento_atual = (
            TelaOrcamentoComplemento(
                parent=self.conteudo,
                voltar_callback=self.tela_inicial
            )
        )
    def tela_documentos(self):

        self.submenu_orcamento.place_forget()

        self.limpar_conteudo()

        self.tela_documentos_atual = TelaDocumentos(
            parent=self.conteudo,
            voltar_callback=self.tela_inicial
        )
