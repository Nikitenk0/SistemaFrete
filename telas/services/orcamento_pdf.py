from tkinter import filedialog, messagebox

from application.ports.gerador_orcamento_pdf import (
    GeradorOrcamentoPdf
)
from domain.models.resultado_orcamento import ResultadoOrcamento
from domain.models.resultado_rota import ResultadoRota


class OrcamentoPdfService:

    def __init__(
        self,
        gerador_pdf: GeradorOrcamentoPdf
    ):
        self._gerador_pdf = gerador_pdf

    def gerar(
        self,
        resultado_rota: ResultadoRota,
        resultado_orcamento: ResultadoOrcamento,
        quantidade_eixos: int,
        calcular_volta: bool
    ) -> None:

        caminho = filedialog.asksaveasfilename(
            title="Salvar orçamento",
            defaultextension=".pdf",
            filetypes=[
                ("Arquivo PDF", "*.pdf")
            ],
            initialfile="orcamento.pdf"
        )

        if not caminho:
            return

        try:

            self._gerador_pdf.gerar(
                resultado_rota=resultado_rota,
                resultado_orcamento=resultado_orcamento,
                quantidade_eixos=quantidade_eixos,
                calcular_volta=calcular_volta,
                caminho=caminho
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro",
                (
                    "Não foi possível gerar o PDF."
                    f"\n\n{erro}"
                )
            )

            return

        messagebox.showinfo(
            "Sucesso",
            "Orçamento gerado com sucesso!"
        )