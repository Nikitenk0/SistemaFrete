import customtkinter as ctk

from application.use_cases.calcular_orcamento_fechado import (
    CalcularOrcamentoFechado
)
from infrastructure.qualp.pesquisador_rota_qualp import PesquisadorRotaQualP
from presentation.desktop.menu_principal import MenuPrincipal
from presentation.desktop.controllers.orcamento_pdf import OrcamentoPdfController
from infrastructure.pdf.gerador_orcamento_reportlab import (
    GeradorOrcamentoPdfReportLab
)

def criar_aplicacao():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    janela = ctk.CTk()

    pesquisador_rota = PesquisadorRotaQualP()

    calcular_orcamento_fechado = (
        CalcularOrcamentoFechado(
            pesquisador_rota=pesquisador_rota
        )
    )

    gerador_orcamento_pdf = (
        GeradorOrcamentoPdfReportLab()
    )

    orcamento_pdf_controller = OrcamentoPdfController(
        gerador_pdf=gerador_orcamento_pdf
    )

    MenuPrincipal(
        master=janela,
        orcamento_callback=(
            calcular_orcamento_fechado.executar
        ),
        pdf_callback=orcamento_pdf_controller.gerar
    )

    return janela


def main():

    janela = criar_aplicacao()

    janela.mainloop()


if __name__ == "__main__":
    main()