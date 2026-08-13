import customtkinter as ctk
from domain.models.resultado_orcamento import ResultadoOrcamento
from domain.models.resultado_rota import ResultadoRota
from tkinter import messagebox, filedialog, LEFT, RIGHT, BOTH, Y, X
from telas.estilos import *
from services.qualp.qualp import QualP
from telas.tela_orcamento_fechada import TelaOrcamentoFechada
from utils.gerador_pdf import gerar_orcamento_pdf
from application.use_cases.calcular_orcamento_fechado import CalcularOrcamentoFechado


class MenuPrincipal:

    def __init__(self, master):

        self.master = master
        
        self.qualp = QualP()

        self.calcular_orcamento_fechado = (
            CalcularOrcamentoFechado(
                pesquisar_rota=self.qualp.pesquisar
            )
        )
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
            orcamento_callback=(
                self.calcular_orcamento_fechado.executar
            ),
            pdf_callback=self.gerar_pdf,
            voltar_callback=self.tela_inicial
        )

    def tela_complemento(self):

        # Fecha o submenu
        self.submenu_orcamento.place_forget()

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

    def tela_documentos(self):

        # Fecha o submenu
        self.submenu_orcamento.place_forget()


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


    def gerar_pdf(
                self,
                resultado_rota: ResultadoRota,
                 resultado_orcamento: ResultadoOrcamento,
                 quantidade_eixos: int,
                calcular_volta: bool
                ):


        # ==========================================================
        # ESCOLHER ONDE SALVAR
        # ==========================================================

        caminho = filedialog.asksaveasfilename(
            title="Salvar orçamento",
            defaultextension=".pdf",
            filetypes=[
                ("Arquivo PDF", "*.pdf")
            ],
            initialfile="orcamento.pdf"
        )

        # Usuário cancelou
        if not caminho:
            return

        # ==========================================================
        # GERA O PDF
        # ==========================================================

        try:

            gerar_orcamento_pdf(
                resultado_rota=resultado_rota,
                resultado_orcamento=resultado_orcamento,
                quantidade_eixos=quantidade_eixos,
                calcular_volta=calcular_volta,
                caminho=caminho
            )

            messagebox.showinfo(
                "Sucesso",
                "Orçamento gerado com sucesso!"
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                f"Não foi possível gerar o PDF.\n\n{erro}"
            )