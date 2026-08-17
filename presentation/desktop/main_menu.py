import customtkinter as ctk

from tkinter import LEFT, RIGHT, BOTH, Y, X

from presentation.desktop.styles import (
    WINDOW_HEIGHT,
    BUTTON_COLOR,
    BACKGROUND_COLOR,
    MENU_COLOR,
    BUTTON_FONT,
    TITLE_FONT,
    WINDOW_WIDTH,
    MENU_WIDTH,
)
from presentation.desktop.closed_load_quote_view import (
    ClosedLoadQuoteView
)
from presentation.desktop.documents_view import DocumentsView
from presentation.desktop.tela_orcamento_complemento import TelaOrcamentoComplemento



class MainMenu:

    def __init__(
        self,
        master,
        calculate_quote_callback,
        generate_pdf_callback
    ):
        self.master = master
        self.calculate_quote_callback = calculate_quote_callback
        self.generate_pdf_callback = generate_pdf_callback

        self.master.title("Sistema")
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.master.configure(fg_color=BACKGROUND_COLOR)

        # ==========================
        # MENU
        # ==========================

        self.menu = ctk.CTkFrame(
            master,
            fg_color=MENU_COLOR,
            width=MENU_WIDTH
        )

        self.menu.pack(side=LEFT, fill=Y)
        self.menu.pack_propagate(False)

        # ==========================
        # CONTEÚDO
        # ==========================

        self.content = ctk.CTkFrame(
            master,
            fg_color=BACKGROUND_COLOR
        )

        self.content.pack(
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



        # ==========================
        # SUBMENU ORÇAMENTO
        # ==========================

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

        # ==========================
        # BOTÃO DOCUMENTOS
        # ==========================


        ctk.CTkButton(
            self.menu,
            text="Documentos",
            command=self.show_documents,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        ).pack(fill=X, pady=5, padx=10)

        self.show_home()

    # ====================================

    def clear_content(self):
        """Remove todos os componentes da área principal."""
        for widget in self.content.winfo_children():
            widget.destroy()

    # ====================================

    def show_home(self):

        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="Sistema",
            font=TITLE_FONT,
            fg_color=BACKGROUND_COLOR
        ).pack(pady=50)

    # ====================================

    def toggle_quote_submenu(self):

        if self.quote_submenu.winfo_ismapped():

            self.quote_submenu.place_forget()

        else:

            self.quote_submenu.place(
                x=MENU_WIDTH,
                y=0
            )


    def show_closed_load_quote(self):

        # Fecha o submenu
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
    def show_documents(self):

        self.quote_submenu.place_forget()

        self.clear_content()

        self.current_documents_view = DocumentsView(
            parent=self.content,
            navigate_back=self.show_home
        )
