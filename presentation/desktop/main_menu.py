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
from presentation.desktop.freight_detail_view import (
    FreightDetailView
)
from presentation.desktop.freight_list_view import (
    FreightListView
)
from presentation.desktop.tela_orcamento_complemento import (
    TelaOrcamentoComplemento
)
from presentation.desktop.vehicle_list_view import (
    VehicleListView
)
from presentation.desktop.transport_provider_list_view import (
    TransportProviderListView
)


class MainMenu:

    def __init__(
        self,
        master,
        calculate_quote_callback,
        generate_pdf_callback,
        list_freights_callback,
        get_freight_details_callback,
        add_transport_unit_callback,
        remove_transport_unit_callback,
        add_vehicle_callback,
        remove_vehicle_callback,
        replace_vehicle_callback,
        search_available_vehicles_callback,
        search_available_drivers_callback,
        create_driver_callback,
        list_drivers_callback,
        get_driver_callback,
        update_driver_callback,
        create_vehicle_callback,
        search_vehicles_callback,
        get_vehicle_callback,
        update_vehicle_callback,
        create_transport_provider_callback,
        search_transport_providers_callback,
        get_transport_provider_callback,
        update_transport_provider_callback,
        get_transport_provider_details_callback,
        set_driver_transport_provider_affiliation_callback,
        set_vehicle_transport_provider_affiliation_callback,
        assign_driver_callback,
        replace_driver_callback,
        finish_driver_callback,
        adopt_current_operational_assignment_callback,
        replace_in_progress_operational_assignment_callback,
        start_freight_callback,
        complete_freight_callback,
    ):
        self.master = master
        self.calculate_quote_callback = calculate_quote_callback
        self.generate_pdf_callback = generate_pdf_callback
        self.list_freights_callback = list_freights_callback
        self.get_freight_details_callback = (
            get_freight_details_callback
        )
        self.add_transport_unit_callback = (
            add_transport_unit_callback
        )
        self.remove_transport_unit_callback = (
            remove_transport_unit_callback
        )
        self.add_vehicle_callback = add_vehicle_callback
        self.remove_vehicle_callback = remove_vehicle_callback
        self.replace_vehicle_callback = replace_vehicle_callback
        self.search_available_vehicles_callback = (
            search_available_vehicles_callback
        )
        self.search_available_drivers_callback = (
            search_available_drivers_callback
        )
        self.create_driver_callback = create_driver_callback
        self.list_drivers_callback = list_drivers_callback
        self.get_driver_callback = get_driver_callback
        self.update_driver_callback = update_driver_callback
        self.create_vehicle_callback = create_vehicle_callback
        self.search_vehicles_callback = search_vehicles_callback
        self.get_vehicle_callback = get_vehicle_callback
        self.update_vehicle_callback = update_vehicle_callback
        self.create_transport_provider_callback = (
            create_transport_provider_callback
        )
        self.search_transport_providers_callback = (
            search_transport_providers_callback
        )
        self.get_transport_provider_callback = (
            get_transport_provider_callback
        )
        self.update_transport_provider_callback = (
            update_transport_provider_callback
        )
        self.get_transport_provider_details_callback = (
            get_transport_provider_details_callback
        )
        self.set_driver_transport_provider_affiliation_callback = (
            set_driver_transport_provider_affiliation_callback
        )
        self.set_vehicle_transport_provider_affiliation_callback = (
            set_vehicle_transport_provider_affiliation_callback
        )
        self.assign_driver_callback = assign_driver_callback
        self.replace_driver_callback = replace_driver_callback
        self.finish_driver_callback = finish_driver_callback
        self.adopt_current_operational_assignment_callback = (
            adopt_current_operational_assignment_callback
        )
        self.replace_in_progress_operational_assignment_callback = (
            replace_in_progress_operational_assignment_callback
        )
        self.start_freight_callback = start_freight_callback
        self.complete_freight_callback = complete_freight_callback
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

        self.catalog_button = ctk.CTkButton(
            self.menu,
            text="Cadastros",
            command=self.toggle_catalog_submenu,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        )
        self.catalog_button.pack(
            fill=X,
            pady=5,
            padx=10
        )

        self.catalog_submenu = ctk.CTkFrame(
            self.master,
            fg_color=MENU_COLOR,
            width=220
        )
        self.catalog_submenu.pack_propagate(False)

        ctk.CTkButton(
            self.catalog_submenu,
            text="2 - Veículos",
            command=self.show_vehicles,
            fg_color=BUTTON_COLOR,
            text_color="white",
            font=BUTTON_FONT
        ).pack(
            fill=X,
            pady=5,
            padx=10
        )

        ctk.CTkButton(
            self.catalog_submenu,
            text="1 - Prestadores",
            command=self.show_transport_providers,
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

    def _hide_submenus(self):

        self.quote_submenu.place_forget()
        self.catalog_submenu.place_forget()

    def toggle_catalog_submenu(self):

        self.quote_submenu.place_forget()

        if self.catalog_submenu.winfo_ismapped():
            self.catalog_submenu.place_forget()
        else:
            self.catalog_submenu.place(
                x=MENU_WIDTH,
                y=0
            )

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

        self.catalog_submenu.place_forget()

        if self.quote_submenu.winfo_ismapped():

            self.quote_submenu.place_forget()

        else:

            self.quote_submenu.place(
                x=MENU_WIDTH,
                y=0
            )

    def show_closed_load_quote(self):

        self._hide_submenus()

        self.clear_content()

        self.current_closed_load_quote_view = ClosedLoadQuoteView(
            self.content,
            calculate_quote_callback=self.calculate_quote_callback,
            generate_pdf_callback=self.generate_pdf_callback,
            navigate_back=self.show_home
        )

    def show_complement(self):

        self._hide_submenus()

        self.clear_content()

        self.tela_complemento_atual = (
            TelaOrcamentoComplemento(
                parent=self.content,
                navigate_back=self.show_home
            )
        )

    def show_freights(self):

        self._hide_submenus()

        self.clear_content()

        self.current_freight_list_view = (
            FreightListView(
                parent=self.content,
                list_freights_callback=(
                    self.list_freights_callback
                ),
                open_freight_callback=(
                    self.show_freight_details
                ),
                navigate_back=self.show_home,
            )
        )

    def show_freight_details(
        self,
        freight_id: int,
    ):

        self._hide_submenus()

        self.clear_content()

        self.current_freight_detail_view = (
            FreightDetailView(
                parent=self.content,
                freight_id=freight_id,
                get_freight_details_callback=(
                    self.get_freight_details_callback
                ),
                add_transport_unit_callback=(
                    self.add_transport_unit_callback
                ),
                remove_transport_unit_callback=(
                    self.remove_transport_unit_callback
                ),
                add_vehicle_callback=(
                    self.add_vehicle_callback
                ),
                remove_vehicle_callback=(
                    self.remove_vehicle_callback
                ),
                replace_vehicle_callback=(
                    self.replace_vehicle_callback
                ),
                search_available_vehicles_callback=(
                    self.search_available_vehicles_callback
                ),
                search_available_drivers_callback=(
                    self.search_available_drivers_callback
                ),
                search_transport_providers_callback=(
                    self.search_transport_providers_callback
                ),
                get_transport_provider_details_callback=(
                    self.get_transport_provider_details_callback
                ),
                assign_driver_callback=(
                    self.assign_driver_callback
                ),
                replace_driver_callback=(
                    self.replace_driver_callback
                ),
                finish_driver_callback=(
                    self.finish_driver_callback
                ),
                adopt_current_operational_assignment_callback=(
                    self.adopt_current_operational_assignment_callback
                ),
                replace_in_progress_operational_assignment_callback=(
                    self.replace_in_progress_operational_assignment_callback
                ),
                start_freight_callback=(
                    self.start_freight_callback
                ),
                complete_freight_callback=(
                    self.complete_freight_callback
                ),
                navigate_back=self.show_freights,
            )
        )

    def show_vehicles(self):

        self._hide_submenus()
        self.clear_content()

        self.current_vehicle_list_view = VehicleListView(
            parent=self.content,
            search_vehicles_callback=(
                self.search_vehicles_callback
            ),
            get_vehicle_callback=(
                self.get_vehicle_callback
            ),
            create_vehicle_callback=(
                self.create_vehicle_callback
            ),
            update_vehicle_callback=(
                self.update_vehicle_callback
            ),
            navigate_back=self.show_home,
        )

    def show_transport_providers(self):

        self._hide_submenus()
        self.clear_content()

        self.current_transport_provider_list_view = (
            TransportProviderListView(
                parent=self.content,
                search_transport_providers_callback=(
                    self.search_transport_providers_callback
                ),
                get_transport_provider_callback=(
                    self.get_transport_provider_callback
                ),
                create_transport_provider_callback=(
                    self.create_transport_provider_callback
                ),
                update_transport_provider_callback=(
                    self.update_transport_provider_callback
                ),
                get_transport_provider_details_callback=(
                    self.get_transport_provider_details_callback
                ),
                set_driver_transport_provider_affiliation_callback=(
                    self.set_driver_transport_provider_affiliation_callback
                ),
                set_vehicle_transport_provider_affiliation_callback=(
                    self.set_vehicle_transport_provider_affiliation_callback
                ),
                create_driver_callback=(
                    self.create_driver_callback
                ),
                get_driver_callback=(
                    self.get_driver_callback
                ),
                update_driver_callback=(
                    self.update_driver_callback
                ),
                list_drivers_callback=(
                    self.list_drivers_callback
                ),
                search_vehicles_callback=(
                    self.search_vehicles_callback
                ),
                navigate_back=self.show_home,
            )
        )

    def show_documents(self):

        self._hide_submenus()

        self.clear_content()

        self.current_documents_view = DocumentsView(
            parent=self.content,
            navigate_back=self.show_home
        )
