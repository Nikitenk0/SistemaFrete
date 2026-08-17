import customtkinter as ctk

from application.use_cases.calculate_closed_load_quote import (
    CalculateClosedLoadQuote
)
from infrastructure.qualp.qualp_route_searcher import QualPRouteSearcher
from presentation.desktop.menu_principal import MenuPrincipal
from presentation.desktop.controllers.orcamento_pdf import OrcamentoPdfController
from infrastructure.pdf.reportlab_quote_pdf_generator import (
    ReportLabQuotePdfGenerator
)

def criar_aplicacao():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    janela = ctk.CTk()

    route_searcher = QualPRouteSearcher()

    calculate_closed_load_quote = (
        CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )
    )

    gerador_orcamento_pdf = (
        ReportLabQuotePdfGenerator()
    )

    orcamento_pdf_controller = OrcamentoPdfController(
        gerador_pdf=gerador_orcamento_pdf
    )

    MenuPrincipal(
        master=janela,
        orcamento_callback=(
            calculate_closed_load_quote.execute
        ),
        pdf_callback=orcamento_pdf_controller.gerar
    )

    return janela


def main():

    janela = criar_aplicacao()

    janela.mainloop()


if __name__ == "__main__":
    main()