import customtkinter as ctk

from tkinter import LEFT, RIGHT, BOTH, Y, X

from presentation.desktop.styles import (
    WINDOW_HEIGHT,
    BUTTON_COLOR,
    BUTTON_HOVER_COLOR,
    BACKGROUND_COLOR,
    MENU_COLOR,
    TEXT_COLOR,
    BUTTON_FONT,
    TITLE_FONT,
    WINDOW_WIDTH,
    MENU_WIDTH,
)
from presentation.desktop.closed_load_quote_view import (
    ClosedLoadQuoteView
)
from presentation.desktop.documents_view import DocumentsView
from presentation.desktop.freight_list_view import (
    FreightListView
)
from presentation.desktop.tela_orcamento_complemento import (
    TelaOrcamentoComplemento
)


class MainMenu:

    def __init__(
        self,
        master,
        calculate_quote_callback,
        generate_pdf_callback,
        list_freights_callback,
    ):
        self.master = master
        self.calculate_quote_callback = calculate_quote_callback
        self.generate_pdf_callback = generate_pdf_callback
        self.list_freights_callback = list_freights_callback
        self.is_dark_mode = False

        self.master.title("Sistema")
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.configure(fg_color=BACKGROUND_COLOR)

        self.menu = ctk.CTkFrame(
            master,
            fg_color=MENU_COLOR,
            width=MENU_WIDTH
        )

        self.menu.pack(side=LEFT, fill=Y)
        self.menu.pack_propagate(False)

        self.content = ctk.CTkFrame(
            master,
            fg_color=BACKGROUND_COLOR
        )

        self.content.pack(
            side=RIGHT,
            expand=True,
            fill=BOTH
        )

        self.quote_button = ctk.CTkButton(
            self.menu,
            text="Orçamento",
            command=self.toggle_quote_submenu,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        )

        self.quote_button.pack(
            fill=X,
            pady=5,
            padx=10
        )

        self.quote_submenu = ctk.CTkFrame(
            self.master,
            fg_color=MENU_COLOR,
            width=220
        )
        self.quote_submenu.pack_propagate(
            False
        )

        ctk.CTkButton(
            self.quote_submenu,
            text="1 - Carga Fechada",
            command=self.show_closed_load_quote,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )

        ctk.CTkButton(
            self.quote_submenu,
            text="2 - Complemento",
            command=self.show_complement,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )

        ctk.CTkButton(
            self.menu,
            text="Fretes",
            command=self.show_freights,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )

        ctk.CTkButton(
            self.menu,
            text="Documentos",
            command=self.show_documents,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )

        self.theme_button = ctk.CTkButton(
            self.menu,
            text="Tema escuro",
            command=self.toggle_appearance_mode,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color=TEXT_COLOR,
            font=BUTTON_FONT
        )

        self.theme_button.pack(
            side="bottom",
            fill=X,
            padx=10,
            pady=10
        )

        self.show_home()

    def toggle_appearance_mode(self):

        if self.is_dark_mode:

            ctk.set_appearance_mode(
                "light"
            )

            self.theme_button.configure(
                text="Tema escuro"
            )

            self.is_dark_mode = False

        else:

            ctk.set_appearance_mode(
                "dark"
            )

            self.theme_button.configure(
                text="Tema claro"
            )

            self.is_dark_mode = True

    def clear_content(self):
        """Remove todos os componentes da área principal."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_home(self):

        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="Sistema",
            font=TITLE_FONT,
            fg_color=BACKGROUND_COLOR
        ).pack(pady=50)

    def toggle_quote_submenu(self):

        if self.quote_submenu.winfo_ismapped():

            self.quote_submenu.place_forget()

        else:

            self.quote_submenu.place(
                x=MENU_WIDTH,
                y=0
            )

    def show_closed_load_quote(self):

        self.quote_submenu.place_forget()

        self.clear_content()

        self.current_closed_load_quote_view = ClosedLoadQuoteView(
            self.content,
            calculate_quote_callback=self.calculate_quote_callback,
            generate_pdf_callback=self.generate_pdf_callback,
            navigate_back=self.show_home
        )

    def show_complement(self):

        self.quote_submenu.place_forget()

        self.clear_content()

        self.tela_complemento_atual = (
            TelaOrcamentoComplemento(
                parent=self.content,
                navigate_back=self.show_home
            )
        )

    def show_freights(self):

        self.quote_submenu.place_forget()

        self.clear_content()

        self.current_freight_list_view = (
            FreightListView(
                parent=self.content,
                list_freights_callback=(
                    self.list_freights_callback
                ),
                navigate_back=self.show_home,
            )
        )

    def show_documents(self):

        self.quote_submenu.place_forget()

        self.clear_content()

        self.current_documents_view = DocumentsView(
            parent=self.content,
            navigate_back=self.show_home
        )
