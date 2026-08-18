import customtkinter as ctk

from config.app import (
    QUALP_EMAIL,
    QUALP_PASSWORD,
    QUALP_HEADLESS,
)
from infrastructure.qualp.qualp_route_searcher import QualPRouteSearcher
from presentation.desktop.main_menu import MainMenu
from presentation.desktop.controllers.quote_pdf_controller import (
    QuotePdfController
)
from infrastructure.pdf.reportlab_quote_pdf_generator import (
    ReportLabQuotePdfGenerator
)
from application.use_cases.calculate_closed_load_quote import (
    CalculateClosedLoadQuote
)
from application.use_cases.generate_quote_pdf import (
    GenerateQuotePdf
)

def create_application():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()

    route_searcher = QualPRouteSearcher(
        email=QUALP_EMAIL,
        password=QUALP_PASSWORD,
        headless=QUALP_HEADLESS
    )

    calculate_closed_load_quote = (
        CalculateClosedLoadQuote(
            route_searcher=route_searcher
        )
    )

    quote_pdf_generator = (
        ReportLabQuotePdfGenerator()
    )

    generate_quote_pdf = GenerateQuotePdf(
        pdf_generator=quote_pdf_generator
    )

    quote_pdf_controller = QuotePdfController(
        generate_quote_pdf=generate_quote_pdf
    )

    quote_pdf_controller = QuotePdfController(
        generate_quote_pdf=generate_quote_pdf
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