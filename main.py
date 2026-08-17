import customtkinter as ctk

from application.use_cases.calculate_closed_load_quote import (
    CalculateClosedLoadQuote
)
from infrastructure.qualp.qualp_route_searcher import QualPRouteSearcher
from presentation.desktop.main_menu import MainMenu
from presentation.desktop.controllers.quote_pdf_controller import (
    QuotePdfController
)
from infrastructure.pdf.reportlab_quote_pdf_generator import (
    ReportLabQuotePdfGenerator
)

def create_application():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()

    route_searcher = QualPRouteSearcher()

    calculate_closed_load_quote = (
        CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )
    )

    quote_pdf_generator = (
        ReportLabQuotePdfGenerator()
    )

    quote_pdf_controller = QuotePdfController(
        pdf_generator=quote_pdf_generator
    )

    MainMenu(
        master=window,
        calculate_quote_callback=(
            calculate_closed_load_quote.execute
        ),
        generate_pdf_callback=quote_pdf_controller.generate
    )

    return window


def main():

    window = create_application()

    window.mainloop()


if __name__ == "__main__":
    main()