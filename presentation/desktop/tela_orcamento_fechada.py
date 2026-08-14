import customtkinter as ctk
from domain.models.resultado_rota import ResultadoRota
from domain.models.resultado_orcamento import ResultadoOrcamento
from utils.conversao_monetaria import converter_valor_monetario
from application.exceptions import (
        DadosOrcamentoInvalidos,
        FalhaCalculoOrcamento,
        FalhaPesquisaRota,
        RotaNaoEncontrada,
    )

class TelaOrcamentoFechada:

    def __init__(
        self,
        parent,
        orcamento_callback,
        pdf_callback,
        voltar_callback
    ):
        self.resultado_rota_atual: ResultadoRota | None = None
        self.resultado_orcamento_atual: ResultadoOrcamento | None = None
        self.parent = parent
        self.orcamento_callback = orcamento_callback
        self.pdf_callback = pdf_callback
        self.voltar_callback = voltar_callback

        self.criar_tela()

    # ==========================================================
    # CRIAÇÃO DA TELA
    # ==========================================================

    def criar_tela(self):

        # Permite que o conteúdo ocupe toda a área disponível.
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self.frame_principal = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        self.frame_principal.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=30,
            pady=20
        )

        self.frame_principal.grid_columnconfigure(
            0,
            weight=1
        )

        # ======================================================
        # TÍTULO
        # ======================================================

        ctk.CTkLabel(
            self.frame_principal,
            text="ORÇAMENTO",
            font=("Arial", 22, "bold")
        ).grid(
            row=0,
            column=0,
            pady=(0, 5)
        )

        ctk.CTkLabel(
            self.frame_principal,
            text="Aqui ficarão os campos do orçamento.",
            font=("Arial", 12)
        ).grid(
            row=1,
            column=0,
            pady=(0, 30)
        )

        # ======================================================
        # FORMULÁRIO
        # ======================================================

        self.criar_formulario()

        # ======================================================
        # SEPARADOR / ESPAÇO
        # ======================================================

        self.frame_separador = ctk.CTkFrame(
            self.frame_principal,
            height=2,
            fg_color=("gray85", "gray25")
        )

        self.frame_separador.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(25, 20)
        )

        # ======================================================
        # ÁREA INFERIOR
        # ======================================================

        self.frame_inferior = ctk.CTkFrame(
            self.frame_principal,
            fg_color="transparent"
        )

        self.frame_inferior.grid(
            row=4,
            column=0,
            sticky="ew"
        )

        # Resultados ocupam um pouco mais de espaço.
        self.frame_inferior.grid_columnconfigure(
            0,
            weight=2
        )

        # Botões.
        self.frame_inferior.grid_columnconfigure(
            1,
            weight=1
        )

        # Espaço vazio à direita, semelhante à imagem 1.
        self.frame_inferior.grid_columnconfigure(
            2,
            weight=1
        )

        self.criar_resultados()
        self.criar_botoes()

    # ==========================================================
    # FORMULÁRIO
    # ==========================================================

    def criar_formulario(self):

        self.frame_formulario = ctk.CTkFrame(
            self.frame_principal,
            fg_color="transparent"
        )

        self.frame_formulario.grid(
            row=2,
            column=0,
            sticky="ew"
        )

        # 4 colunas iguais.
        for coluna in range(4):

            self.frame_formulario.grid_columnconfigure(
                coluna,
                weight=1
            )

        # ======================================================
        # ORIGEM
        # ======================================================

        ctk.CTkLabel(
            self.frame_formulario,
            text="Origem",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=0,
            pady=(0, 5)
        )

        self.txt_origem = ctk.CTkEntry(
            self.frame_formulario,
            width=180
        )

        self.txt_origem.grid(
            row=1,
            column=0,
            padx=10
        )

        self.txt_origem.bind(
            "<KeyRelease>",
            self.validar_campos
        )

        # ======================================================
        # DESTINO
        # ======================================================

        ctk.CTkLabel(
            self.frame_formulario,
            text="Destino",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=1,
            pady=(0, 5)
        )

        self.txt_destino = ctk.CTkEntry(
            self.frame_formulario,
            width=180
        )

        self.txt_destino.grid(
            row=1,
            column=1,
            padx=10
        )

        self.txt_destino.bind(
            "<KeyRelease>",
            self.validar_campos
        )

        # ======================================================
        # QUANTIDADE DE EIXOS
        # ======================================================

        ctk.CTkLabel(
            self.frame_formulario,
            text="Quantidade de eixos",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=2,
            pady=(0, 5)
        )

        self.txt_eixos = ctk.CTkComboBox(
            self.frame_formulario,
            values=[
                str(i)
                for i in range(2, 10)
            ],
            width=100,
            state="readonly"
        )

        self.txt_eixos.grid(
            row=1,
            column=2,
            padx=10
        )

        self.txt_eixos.set("6")

        # ======================================================
        # VALOR DA NOTA
        # ======================================================

        ctk.CTkLabel(
            self.frame_formulario,
            text="Valor de Nota",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=3,
            pady=(0, 5)
        )

        self.txt_valor_nota = ctk.CTkEntry(
            self.frame_formulario,
            width=180,
            placeholder_text="Ex.: 150000"
        )

        self.txt_valor_nota.grid(
            row=1,
            column=3,
            padx=10
        )

        self.txt_valor_nota.bind(
            "<KeyRelease>",
            self.validar_campos
        )

        # ======================================================
        # CALCULAR VOLTA
        # ======================================================

        self.var_calcular_volta = ctk.BooleanVar(
            value=False
        )

        self.switch_volta = ctk.CTkSwitch(
            self.frame_formulario,
            text="Calcular Volta",
            variable=self.var_calcular_volta,
            font=("Arial", 12)
        )

        self.switch_volta.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="w",
            padx=20,
            pady=(20, 0)
        )

    # ==========================================================
    # RESULTADOS
    # ==========================================================

    def criar_resultados(self):

        self.frame_resultado = ctk.CTkFrame(
            self.frame_inferior,
            fg_color="transparent"
        )

        self.frame_resultado.grid(
            row=0,
            column=0,
            sticky="nw",
            padx=(40, 20)
        )

        self.frame_resultado.grid_columnconfigure(
            0,
            minsize=100
        )

        self.frame_resultado.grid_columnconfigure(
            1,
            minsize=180
        )

        # ======================================================
        # FUNÇÃO AUXILIAR
        # ======================================================

        def criar_linha(
            linha,
            texto,
            negrito=False
        ):

            if negrito:

                fonte = (
                    "Arial",
                    14,
                    "bold"
                )

            else:

                fonte = (
                    "Arial",
                    14
                )

            ctk.CTkLabel(
                self.frame_resultado,
                text=texto,
                font=fonte
            ).grid(
                row=linha,
                column=0,
                sticky="w",
                padx=(0, 15),
                pady=7
            )

            label_valor = ctk.CTkLabel(
                self.frame_resultado,
                text="--",
                font=fonte
            )

            label_valor.grid(
                row=linha,
                column=1,
                sticky="w",
                padx=5,
                pady=7
            )

            return label_valor

        # ======================================================
        # CAMPOS
        # ======================================================

        self.lbl_origem = criar_linha(
            0,
            "Origem"
        )

        self.lbl_destino = criar_linha(
            1,
            "Destino"
        )

        self.lbl_distancia = criar_linha(
            2,
            "Distância"
        )

        self.lbl_pedagio = criar_linha(
            3,
            "Pedágio"
        )

        self.lbl_geral = criar_linha(
            4,
            "Geral",
            negrito=True
        )

        self.lbl_custo = criar_linha(
            5,
            "Custo"
        )

        self.lbl_imposto = criar_linha(
            6,
            "Imposto"
        )

        self.lbl_total = criar_linha(
            7,
            "Total",
            negrito=True
        )

    # ==========================================================
    # BOTÕES
    # ==========================================================

    def criar_botoes(self):

        self.frame_botoes = ctk.CTkFrame(
            self.frame_inferior,
            fg_color="transparent"
        )

        self.frame_botoes.grid(
            row=0,
            column=1,
            sticky="n",
            padx=20,
            pady=(40, 0)
        )

        # ======================================================
        # PESQUISAR
        # ======================================================

        self.btn_pesquisar = ctk.CTkButton(
            self.frame_botoes,
            text="Pesquisar",
            command=self.pesquisar,
            state="disabled",
            width=120,
            height=30
        )

        self.btn_pesquisar.pack(
            pady=5
        )

        # ======================================================
        # GERAR PDF
        # ======================================================

        self.btn_pdf = ctk.CTkButton(
            self.frame_botoes,
            text="Gerar PDF",
            command=self.gerar_pdf,
            state="disabled",
            width=120,
            height=30
        )

        self.btn_pdf.pack(
            pady=5
        )

        # ======================================================
        # VOLTAR
        # ======================================================

        self.btn_voltar = ctk.CTkButton(
            self.frame_botoes,
            text="← Voltar",
            command=self.voltar_callback,
            width=120,
            height=30
        )

        self.btn_voltar.pack(
            pady=5
        )

    # ==========================================================
    # VALIDAÇÃO DOS CAMPOS
    # ==========================================================

    def validar_campos(self, event=None):

        valor_nota = self.txt_valor_nota.get().strip()
        origem = self.txt_origem.get().strip()
        destino = self.txt_destino.get().strip()

        if valor_nota and origem and destino:

            self.btn_pesquisar.configure(
                state="normal"
            )

        else:

            self.btn_pesquisar.configure(
                state="disabled"
            )

    # ==========================================================
    # PESQUISAR
    # ==========================================================

    def pesquisar(self):

        self.limpar_resultados()
        # Desabilita temporariamente para evitar múltiplos cliques.
        self.btn_pesquisar.configure(
            state="disabled"
        )

        valor_nota = self.txt_valor_nota.get().strip()
        origem = self.txt_origem.get().strip()
        destino = self.txt_destino.get().strip()

        try:

            eixos = int(
                self.txt_eixos.get()
            )

        except ValueError:

            self.lbl_total.configure(
                text="Quantidade de eixos inválida"
            )

            self.validar_campos()

            return

        calcular_volta = self.var_calcular_volta.get()

        # ======================================================
        # EXECUTA O CASO DE USO
        # ======================================================
        try:

            resultado = self.orcamento_callback(
                valor_nota=valor_nota,
                origem=origem,
                destino=destino,
                quantidade_eixos=eixos,
                calcular_volta=calcular_volta
            )

        except DadosOrcamentoInvalidos:

            self.lbl_total.configure(
                text="Dados do orçamento inválidos"
            )

            self.validar_campos()

            return

        except RotaNaoEncontrada:

            self.lbl_total.configure(
                text="Nenhuma rota encontrada"
            )

            self.validar_campos()

            return

        except FalhaPesquisaRota:

            self.lbl_total.configure(
                text="Erro ao pesquisar rota"
            )

            self.validar_campos()

            return

        except FalhaCalculoOrcamento:

            self.lbl_total.configure(
                text="Erro ao calcular orçamento"
            )

            self.validar_campos()

            return

        
        resultado_rota = resultado.rota
        resultado_orcamento = resultado.orcamento

        self.resultado_rota_atual = resultado_rota
        self.resultado_orcamento_atual = resultado_orcamento
        # ======================================================
        # ATUALIZA RESULTADOS DA ROTA
        # ======================================================

        self.lbl_origem.configure(
            text=resultado_rota.origem
        )

        self.lbl_destino.configure(
            text=resultado_rota.destino
        )

        self.lbl_distancia.configure(
            text=resultado_rota.distancia
        )

        self.lbl_pedagio.configure(
            text=self.formatar_valor_resultado(
                resultado_rota.pedagio
            )
        )

        self.lbl_geral.configure(
            text=self.formatar_valor_resultado(
                resultado_rota.geral
            )
        )

        # ======================================================
        # ATUALIZA CUSTO
        # ======================================================

        self.lbl_custo.configure(
            text=self.formatar_moeda(
                resultado_orcamento.custo
            )
        )

        # ======================================================
        # ATUALIZA IMPOSTO
        # ======================================================

        self.lbl_imposto.configure(
            text=self.formatar_moeda(
                resultado_orcamento.total_impostos
            )
        )

        # ======================================================
        # ATUALIZA TOTAL
        # ======================================================

        self.lbl_total.configure(
            text=self.formatar_moeda(
                resultado_orcamento.total
            )
        )

        # ======================================================
        # HABILITA BOTÕES
        # ======================================================

        self.btn_pdf.configure(
            state="normal"
        )

        self.validar_campos()

    # ==========================================================
    # GERAR PDF
    # ==========================================================

    def gerar_pdf(self):

        if (
            self.resultado_rota_atual is None
            or self.resultado_orcamento_atual is None
        ):

            self.lbl_total.configure(
                text="Realize uma pesquisa antes de gerar o PDF"
            )

            self.btn_pdf.configure(
                state="disabled"
            )

            return

        try:

            self.pdf_callback(
                self.resultado_rota_atual,
                self.resultado_orcamento_atual,
                quantidade_eixos=int(
                    self.txt_eixos.get()
                ),
                calcular_volta=self.var_calcular_volta.get()
            )

        except Exception as erro:

            print(
                "ERRO AO GERAR PDF:",
                repr(erro)
            )

            self.lbl_total.configure(
                text="Erro ao gerar PDF"
            )

    # ==========================================================
    # LIMPAR RESULTADOS
    # ==========================================================

    def limpar_resultados(self):

        self.resultado_rota_atual = None
        self.resultado_orcamento_atual = None

        labels = [
            self.lbl_origem,
            self.lbl_destino,
            self.lbl_distancia,
            self.lbl_pedagio,
            self.lbl_geral,
            self.lbl_custo,
            self.lbl_imposto,
            self.lbl_total
        ]

        for label in labels:

            label.configure(
                text="--"
            )

        self.btn_pdf.configure(
            state="disabled"
        )

    # ==========================================================
    # LIMPAR TELA COMPLETA
    # ==========================================================

    def limpar_tela(self):

        self.txt_origem.delete(
            0,
            "end"
        )

        self.txt_destino.delete(
            0,
            "end"
        )

        self.txt_valor_nota.delete(
            0,
            "end"
        )

        self.txt_eixos.set(
            "6"
        )

        self.var_calcular_volta.set(
            False
        )

        self.limpar_resultados()

        self.btn_pesquisar.configure(
            state="disabled"
        )

        self.txt_origem.focus_set()


    # ==========================================================
    # FORMATAÇÃO EM REAL
    # ==========================================================

    @staticmethod
    def formatar_moeda(valor):

        try:

            valor = float(
                valor
            )

        except (
            TypeError,
            ValueError
        ):

            return str(
                valor
            )

        valor_formatado = (
            f"{valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return (
            f"R$ {valor_formatado}"
        )

    # ==========================================================
    # FORMATA VALORES RETORNADOS PELA PESQUISA
    # ==========================================================

    def formatar_valor_resultado(
        self,
        valor
    ):

        if valor in (
            None,
            "",
            "--"
        ):

            return "--"

        # Se já vier como string formatada,
        # mantém como está.
        if isinstance(
            valor,
            str
        ):

            texto = valor.strip()

            if texto.startswith(
                "R$"
            ):

                return texto

            # Se não for possível transformar em número,
            # mantém o texto original.
            try:

                numero = converter_valor_monetario(
                    texto
                )

            except ValueError:

                return texto

            return self.formatar_moeda(
                numero
            )

        return self.formatar_moeda(
            valor
        )