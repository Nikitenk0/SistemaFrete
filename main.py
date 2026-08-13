import customtkinter as ctk

from application.use_cases.calcular_orcamento_fechado import (
    CalcularOrcamentoFechado
)
from services.qualp.qualp import QualP
from telas.menu_principal import MenuPrincipal
from telas.services.orcamento_pdf import OrcamentoPdfService


def criar_aplicacao():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    janela = ctk.CTk()

    qualp = QualP()

    calcular_orcamento_fechado = (
        CalcularOrcamentoFechado(
            pesquisar_rota=qualp.pesquisar
        )
    )

    orcamento_pdf_service = OrcamentoPdfService()

    MenuPrincipal(
        master=janela,
        orcamento_callback=(
            calcular_orcamento_fechado.executar
        ),
        pdf_callback=orcamento_pdf_service.gerar
    )

    return janela


def main():

    janela = criar_aplicacao()

    janela.mainloop()


if __name__ == "__main__":
    main()