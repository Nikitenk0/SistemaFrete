import customtkinter as ctk

from domain.models.quote_calculation_result import (
    QuoteCalculationResult
)
from application.dtos.route_result import RouteResult
from application.parsers.monetary_value import parse_monetary_value
from application.exceptions import (
    InvalidQuoteDataError,
    QuoteCalculationError,
    RouteNotFoundError,
    RouteSearchError,
)


class ClosedLoadQuoteView:

    def __init__(
        self,
        parent,
        calculate_quote_callback,
        generate_pdf_callback,
        navigate_back
    ):
        self.current_route_result: RouteResult | None = None
        self.current_quote_result: QuoteCalculationResult | None = None

        self.parent = parent
        self.calculate_quote_callback = calculate_quote_callback
        self.generate_pdf_callback = generate_pdf_callback
        self.navigate_back = navigate_back

        self.build()

    # ==========================================================
    # CRIAÇÃO DA TELA
    # ==========================================================

    def build(self):

        # Permite que o conteúdo ocupe toda a área disponível.
        self.parent.grid_rowconfigure(
            0,
            weight=1
        )

        self.parent.grid_columnconfigure(
            0,
            weight=1
        )

        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        self.main_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=30,
            pady=20
        )

        self.main_frame.grid_columnconfigure(
            0,
            weight=1
        )

        # ======================================================
        # TÍTULO
        # ======================================================

        ctk.CTkLabel(
            self.main_frame,
            text="ORÇAMENTO",
            font=("Arial", 22, "bold")
        ).grid(
            row=0,
            column=0,
            pady=(0, 5)
        )

        ctk.CTkLabel(
            self.main_frame,
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

        self.build_form()

        # ======================================================
        # SEPARADOR / ESPAÇO
        # ======================================================

        self.separator_frame = ctk.CTkFrame(
            self.main_frame,
            height=2,
            fg_color=("gray85", "gray25")
        )

        self.separator_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(25, 20)
        )

        # ======================================================
        # ÁREA INFERIOR
        # ======================================================

        self.bottom_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.bottom_frame.grid(
            row=4,
            column=0,
            sticky="ew"
        )

        # Resultados ocupam um pouco mais de espaço.
        self.bottom_frame.grid_columnconfigure(
            0,
            weight=2
        )

        # Botões.
        self.bottom_frame.grid_columnconfigure(
            1,
            weight=1
        )

        # Espaço vazio à direita.
        self.bottom_frame.grid_columnconfigure(
            2,
            weight=1
        )

        self.build_results()
        self.build_buttons()

    # ==========================================================
    # FORMULÁRIO
    # ==========================================================

    def build_form(self):

        self.form_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        self.form_frame.grid(
            row=2,
            column=0,
            sticky="ew"
        )

        # 4 colunas iguais.
        for coluna in range(4):

            self.form_frame.grid_columnconfigure(
                coluna,
                weight=1
            )

        # ======================================================
        # ORIGEM
        # ======================================================

        ctk.CTkLabel(
            self.form_frame,
            text="Origem",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=0,
            pady=(0, 5)
        )

        self.origin_entry = ctk.CTkEntry(
            self.form_frame,
            width=180
        )

        self.origin_entry.grid(
            row=1,
            column=0,
            padx=10
        )

        self.origin_entry.bind(
            "<KeyRelease>",
            self.validate_fields
        )

        # ======================================================
        # DESTINO
        # ======================================================

        ctk.CTkLabel(
            self.form_frame,
            text="Destino",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=1,
            pady=(0, 5)
        )

        self.destination_entry = ctk.CTkEntry(
            self.form_frame,
            width=180
        )

        self.destination_entry.grid(
            row=1,
            column=1,
            padx=10
        )

        self.destination_entry.bind(
            "<KeyRelease>",
            self.validate_fields
        )

        # ======================================================
        # QUANTIDADE DE EIXOS
        # ======================================================

        ctk.CTkLabel(
            self.form_frame,
            text="Quantidade de eixos",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=2,
            pady=(0, 5)
        )

        self.axle_count_combobox = ctk.CTkComboBox(
            self.form_frame,
            values=[
                str(i)
                for i in range(2, 10)
            ],
            width=100,
            state="readonly"
        )

        self.axle_count_combobox.grid(
            row=1,
            column=2,
            padx=10
        )

        self.axle_count_combobox.set(
            "6"
        )

        # ======================================================
        # VALOR DA NOTA
        # ======================================================

        ctk.CTkLabel(
            self.form_frame,
            text="Valor de Nota",
            font=("Arial", 12)
        ).grid(
            row=0,
            column=3,
            pady=(0, 5)
        )

        self.txt_valor_nota = ctk.CTkEntry(
            self.form_frame,
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
            self.validate_fields
        )

        # ======================================================
        # CALCULAR VOLTA
        # ======================================================

        self.include_return_trip_var = ctk.BooleanVar(
            value=False
        )

        self.round_trip_switch = ctk.CTkSwitch(
            self.form_frame,
            text="Calcular Volta",
            variable=self.include_return_trip_var,
            font=("Arial", 12)
        )

        self.round_trip_switch.grid(
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

    def build_results(self):

        self.results_frame = ctk.CTkFrame(
            self.bottom_frame,
            fg_color="transparent"
        )

        self.results_frame.grid(
            row=0,
            column=0,
            sticky="nw",
            padx=(40, 20)
        )

        self.results_frame.grid_columnconfigure(
            0,
            minsize=100
        )

        self.results_frame.grid_columnconfigure(
            1,
            minsize=180
        )

        # ======================================================
        # FUNÇÃO AUXILIAR
        # ======================================================

        def create_result_row(
            row,
            text,
            bold=False
        ):

            if bold:

                font = (
                    "Arial",
                    14,
                    "bold"
                )

            else:

                font = (
                    "Arial",
                    14
                )

            ctk.CTkLabel(
                self.results_frame,
                text=text,
                font=font
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=(0, 15),
                pady=7
            )

            value_label = ctk.CTkLabel(
                self.results_frame,
                text="--",
                font=font
            )

            value_label.grid(
                row=row,
                column=1,
                sticky="w",
                padx=5,
                pady=7
            )

            return value_label

        # ======================================================
        # CAMPOS
        # ======================================================

        self.origin_value_label = create_result_row(
            0,
            "Origem"
        )

        self.destination_value_label = create_result_row(
            1,
            "Destino"
        )

        self.distance_value_label = create_result_row(
            2,
            "Distância"
        )

        self.toll_value_label = create_result_row(
            3,
            "Pedágio"
        )

        self.lbl_geral = create_result_row(
            4,
            "Geral",
            bold=True
        )

        self.lbl_custo = create_result_row(
            5,
            "Custo"
        )

        self.tax_value_label = create_result_row(
            6,
            "Imposto"
        )

        self.total_value_label = create_result_row(
            7,
            "Total",
            bold=True
        )

    # ==========================================================
    # BOTÕES
    # ==========================================================

    def build_buttons(self):

        self.buttons_frame = ctk.CTkFrame(
            self.bottom_frame,
            fg_color="transparent"
        )

        self.buttons_frame.grid(
            row=0,
            column=1,
            sticky="n",
            padx=20,
            pady=(40, 0)
        )

        # ======================================================
        # PESQUISAR
        # ======================================================

        self.calculate_button = ctk.CTkButton(
            self.buttons_frame,
            text="Pesquisar",
            command=self.calculate_quote,
            state="disabled",
            width=120,
            height=30
        )

        self.calculate_button.pack(
            pady=5
        )

        # ======================================================
        # GERAR PDF
        # ======================================================

        self.pdf_button = ctk.CTkButton(
            self.buttons_frame,
            text="Gerar PDF",
            command=self.generate_pdf,
            state="disabled",
            width=120,
            height=30
        )

        self.pdf_button.pack(
            pady=5
        )

        # ======================================================
        # VOLTAR
        # ======================================================

        self.back_button = ctk.CTkButton(
            self.buttons_frame,
            text="← Voltar",
            command=self.navigate_back,
            width=120,
            height=30
        )

        self.back_button.pack(
            pady=5
        )

    # ==========================================================
    # VALIDAÇÃO DOS CAMPOS
    # ==========================================================

    def validate_fields(
        self,
        event=None
    ):

        valor_nota = self.txt_valor_nota.get().strip()
        origem = self.origin_entry.get().strip()
        destino = self.destination_entry.get().strip()

        if valor_nota and origem and destino:

            self.calculate_button.configure(
                state="normal"
            )

        else:

            self.calculate_button.configure(
                state="disabled"
            )

    # ==========================================================
    # CALCULAR ORÇAMENTO
    # ==========================================================

    def calculate_quote(self):

        self.clear_results()

        # Desabilita temporariamente para evitar múltiplos cliques.
        self.calculate_button.configure(
            state="disabled"
        )

        valor_nota = self.txt_valor_nota.get().strip()
        origem = self.origin_entry.get().strip()
        destino = self.destination_entry.get().strip()

        try:

            axle_count = int(
                self.axle_count_combobox.get()
            )

        except ValueError:

            self.total_value_label.configure(
                text="Quantidade de eixos inválida"
            )

            self.validate_fields()

            return

        include_return_trip = self.include_return_trip_var.get()

        # ======================================================
        # EXECUTA O CASO DE USO
        # ======================================================

        try:

            result = self.calculate_quote_callback(
                valor_nota=valor_nota,
                origem=origem,
                destino=destino,
                quantidade_eixos=axle_count,
                calcular_volta=include_return_trip
            )

        except InvalidQuoteDataError:

            self.total_value_label.configure(
                text="Dados do orçamento inválidos"
            )

            self.validate_fields()

            return

        except RouteNotFoundError:

            self.total_value_label.configure(
                text="Nenhuma rota encontrada"
            )

            self.validate_fields()

            return

        except RouteSearchError:

            self.total_value_label.configure(
                text="Erro ao pesquisar rota"
            )

            self.validate_fields()

            return

        except QuoteCalculationError:

            self.total_value_label.configure(
                text="Erro ao calcular orçamento"
            )

            self.validate_fields()

            return

        route_result = result.route_result
        quote_result = result.quote_result

        self.current_route_result = route_result
        self.current_quote_result = quote_result

        # ======================================================
        # ATUALIZA RESULTADOS DA ROTA
        # ======================================================

        self.origin_value_label.configure(
            text=route_result.origem
        )

        self.destination_value_label.configure(
            text=route_result.destino
        )

        self.distance_value_label.configure(
            text=route_result.distancia
        )

        self.toll_value_label.configure(
            text=self.format_result_value(
                route_result.pedagio
            )
        )

        self.lbl_geral.configure(
            text=self.format_result_value(
                route_result.geral
            )
        )

        # ======================================================
        # ATUALIZA CUSTO
        # ======================================================

        self.lbl_custo.configure(
            text=self.format_currency(
                quote_result.custo
            )
        )

        # ======================================================
        # ATUALIZA IMPOSTO
        # ======================================================

        self.tax_value_label.configure(
            text=self.format_currency(
                quote_result.total_impostos
            )
        )

        # ======================================================
        # ATUALIZA TOTAL
        # ======================================================

        self.total_value_label.configure(
            text=self.format_currency(
                quote_result.total
            )
        )

        # ======================================================
        # HABILITA BOTÕES
        # ======================================================

        self.pdf_button.configure(
            state="normal"
        )

        self.validate_fields()

    # ==========================================================
    # GERAR PDF
    # ==========================================================

    def generate_pdf(self):

        if (
            self.current_route_result is None
            or self.current_quote_result is None
        ):

            self.total_value_label.configure(
                text="Realize uma pesquisa antes de gerar o PDF"
            )

            self.pdf_button.configure(
                state="disabled"
            )

            return

        try:

            self.generate_pdf_callback(
                self.current_route_result,
                self.current_quote_result,
                axle_count=int(
                    self.axle_count_combobox.get()
                ),
                include_return_trip=self.include_return_trip_var.get()
            )

        except Exception as error:

            print(
                "ERRO AO GERAR PDF:",
                repr(error)
            )

            self.total_value_label.configure(
                text="Erro ao gerar PDF"
            )

    # ==========================================================
    # LIMPAR RESULTADOS
    # ==========================================================

    def clear_results(self):

        self.current_route_result = None
        self.current_quote_result = None

        labels = [
            self.origin_value_label,
            self.destination_value_label,
            self.distance_value_label,
            self.toll_value_label,
            self.lbl_geral,
            self.lbl_custo,
            self.tax_value_label,
            self.total_value_label
        ]

        for label in labels:

            label.configure(
                text="--"
            )

        self.pdf_button.configure(
            state="disabled"
        )

    # ==========================================================
    # LIMPAR TELA COMPLETA
    # ==========================================================

    def reset(self):

        self.origin_entry.delete(
            0,
            "end"
        )

        self.destination_entry.delete(
            0,
            "end"
        )

        self.txt_valor_nota.delete(
            0,
            "end"
        )

        self.axle_count_combobox.set(
            "6"
        )

        self.include_return_trip_var.set(
            False
        )

        self.clear_results()

        self.calculate_button.configure(
            state="disabled"
        )

        self.origin_entry.focus_set()

    # ==========================================================
    # FORMATAÇÃO EM REAL
    # ==========================================================

    @staticmethod
    def format_currency(value):

        try:

            number = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return str(
                value
            )

        formatted_value = (
            f"{number:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

        return (
            f"R$ {formatted_value}"
        )

    # ==========================================================
    # FORMATA VALORES RETORNADOS PELA PESQUISA
    # ==========================================================

    def format_result_value(
        self,
        value
    ):

        if value in (
            None,
            "",
            "--"
        ):

            return "--"

        # Se já vier como string formatada,
        # mantém como está.
        if isinstance(
            value,
            str
        ):

            text = value.strip()

            if text.startswith(
                "R$"
            ):

                return text

            # Se não for possível transformar em número,
            # mantém o texto original.
            try:

                number = parse_monetary_value(
                    text
                )

            except ValueError:

                return text

            return self.format_currency(
                number
            )

        return self.format_currency(
            value
        )