from tkinter import messagebox, ttk

import customtkinter as ctk

from domain.models.driver_transport_provider_affiliation import (
    DriverTransportProviderRole,
)
from domain.models.transport_provider import (
    TransportProviderType,
)
from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.driver_create_dialog import DriverCreateDialog
from presentation.desktop.driver_edit_dialog import DriverEditDialog
from presentation.desktop.transport_provider_catalog_formatting import (
    driver_role_label,
    format_cpf,
    format_tax_document,
    provider_type_label,
    vehicle_relation_label,
)
from presentation.desktop.transport_provider_driver_link_dialog import (
    TransportProviderDriverLinkDialog,
)
from presentation.desktop.transport_provider_driver_role_dialog import (
    TransportProviderDriverRoleDialog,
)
from presentation.desktop.transport_provider_vehicle_link_dialog import (
    TransportProviderVehicleLinkDialog,
)
from presentation.desktop.vehicle_catalog_formatting import (
    format_vehicle_plate,
    vehicle_type_label,
)


class TransportProviderLinksDialog:

    def __init__(
        self,
        parent,
        transport_provider_id: int,
        get_transport_provider_details_callback,
        set_driver_transport_provider_affiliation_callback,
        set_vehicle_transport_provider_affiliation_callback,
        create_driver_callback,
        get_driver_callback,
        update_driver_callback,
        list_drivers_callback,
        search_vehicles_callback,
    ):
        self._provider_id = transport_provider_id
        self._get_details_callback = (
            get_transport_provider_details_callback
        )
        self._set_driver_affiliation_callback = (
            set_driver_transport_provider_affiliation_callback
        )
        self._set_vehicle_affiliation_callback = (
            set_vehicle_transport_provider_affiliation_callback
        )
        self._create_driver_callback = create_driver_callback
        self._get_driver_callback = get_driver_callback
        self._update_driver_callback = update_driver_callback
        self._list_drivers_callback = list_drivers_callback
        self._search_vehicles_callback = search_vehicles_callback
        self._details = None
        self._is_loading = False

        self._window = ctk.CTkToplevel(parent)
        self._window.title("Vínculos do prestador")
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol("WM_DELETE_WINDOW", self._close)

        self._task_runner = TkAsyncTaskRunner(
            scheduler=self._window
        )

        self._build()
        self._load()
        self._window.wait_window()

    def _build(self) -> None:
        self._window.grid_rowconfigure(0, weight=1)
        self._window.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=18,
            pady=16,
        )
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_rowconfigure(5, weight=1)

        self.title_label = ctk.CTkLabel(
            frame,
            text="PRESTADOR",
            font=("Arial", 18, "bold"),
        )
        self.title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.subtitle_label = ctk.CTkLabel(
            frame,
            text="",
        )
        self.subtitle_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 12),
        )

        driver_header = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        driver_header.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 5),
        )

        ctk.CTkLabel(
            driver_header,
            text="Motoristas vinculados",
            font=("Arial", 14, "bold"),
        ).pack(side="left")

        self.edit_driver_button = ctk.CTkButton(
            driver_header,
            text="Editar motorista",
            width=125,
            state="disabled",
            command=self._edit_driver,
        )
        self.edit_driver_button.pack(
            side="right",
            padx=(8, 0),
        )

        self.link_driver_button = ctk.CTkButton(
            driver_header,
            text="Vincular existente",
            width=125,
            command=self._link_driver,
        )
        self.link_driver_button.pack(
            side="right",
            padx=(8, 0),
        )

        self.create_driver_button = ctk.CTkButton(
            driver_header,
            text="Novo motorista",
            width=120,
            command=self._create_driver,
        )
        self.create_driver_button.pack(side="right")

        self.driver_tree = ttk.Treeview(
            frame,
            columns=("id", "name", "cpf", "role"),
            show="headings",
            height=7,
            selectmode="browse",
        )
        for column, label, width in (
            ("id", "ID", 55),
            ("name", "Motorista", 250),
            ("cpf", "CPF", 130),
            ("role", "Vínculo", 160),
        ):
            self.driver_tree.heading(column, text=label)
            self.driver_tree.column(
                column,
                width=width,
                anchor="center",
            )
        self.driver_tree.grid(
            row=3,
            column=0,
            sticky="nsew",
        )
        self.driver_tree.bind(
            "<<TreeviewSelect>>",
            self._on_driver_selection,
        )
        self.driver_tree.bind(
            "<Double-1>",
            lambda _event: self._edit_driver(),
        )

        vehicle_header = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        vehicle_header.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(12, 5),
        )

        ctk.CTkLabel(
            vehicle_header,
            text="Veículos vinculados",
            font=("Arial", 14, "bold"),
        ).pack(side="left")

        self.link_vehicle_button = ctk.CTkButton(
            vehicle_header,
            text="Vincular veículo",
            width=135,
            command=self._link_vehicle,
        )
        self.link_vehicle_button.pack(side="right")

        self.vehicle_tree = ttk.Treeview(
            frame,
            columns=("id", "plate", "type", "relation"),
            show="headings",
            height=7,
        )
        for column, label, width in (
            ("id", "ID", 55),
            ("plate", "Placa", 120),
            ("type", "Tipo", 240),
            ("relation", "Relação", 140),
        ):
            self.vehicle_tree.heading(column, text=label)
            self.vehicle_tree.column(
                column,
                width=width,
                anchor="center",
            )
        self.vehicle_tree.grid(
            row=5,
            column=0,
            sticky="nsew",
        )

        footer = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        footer.grid(
            row=6,
            column=0,
            sticky="ew",
            pady=(12, 0),
        )

        self.loading_label = ctk.CTkLabel(
            footer,
            text="",
        )
        self.loading_label.pack(side="left")

        ctk.CTkButton(
            footer,
            text="Fechar",
            width=95,
            command=self._close,
        ).pack(side="right")

        self._window.geometry("930x720")

    def _load(self) -> None:
        if self._is_loading:
            return

        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._get_details_callback(
                self._provider_id
            ),
            on_success=self._show_details,
            on_error=self._show_error,
        )

    def _show_details(self, details) -> None:
        self._details = details
        provider = details.provider
        display_name = (
            provider.trade_name
            or provider.legal_name
        )

        self.title_label.configure(
            text=display_name
        )
        self.subtitle_label.configure(
            text=(
                f"{provider_type_label(provider.provider_type)} | "
                f"{format_tax_document(provider.tax_document)}"
            )
        )

        self.driver_tree.delete(
            *self.driver_tree.get_children()
        )
        for item in details.drivers:
            self.driver_tree.insert(
                "",
                "end",
                iid=str(item.driver_id),
                values=(
                    item.driver_id,
                    item.name,
                    format_cpf(item.cpf),
                    driver_role_label(item.role),
                ),
            )

        self.vehicle_tree.delete(
            *self.vehicle_tree.get_children()
        )
        for item in details.vehicles:
            self.vehicle_tree.insert(
                "",
                "end",
                iid=str(item.vehicle_id),
                values=(
                    item.vehicle_id,
                    format_vehicle_plate(item.plate),
                    vehicle_type_label(
                        item.vehicle_type
                    ),
                    vehicle_relation_label(
                        item.relation
                    ),
                ),
            )

        self._set_loading(False)
        self._on_driver_selection()

    def _create_driver(self) -> None:
        if self._is_loading or self._details is None:
            return

        provider = self._details.provider
        is_individual = (
            provider.provider_type
            == TransportProviderType.INDIVIDUAL
        )

        if is_individual and self._details.drivers:
            messagebox.showinfo(
                "Motorista já vinculado",
                (
                    "Prestador pessoa física já possui "
                    "motorista vinculado."
                ),
                parent=self._window,
            )
            return

        dialog = DriverCreateDialog(
            parent=self._window,
            create_driver_callback=(
                self._create_driver_callback
            ),
            initial_name=(
                provider.legal_name
                if is_individual
                else ""
            ),
            initial_cpf=(
                provider.tax_document
                if is_individual
                else ""
            ),
            lock_cpf=is_individual,
        )

        if dialog.result is None:
            return

        driver = dialog.result

        if is_individual:
            role = DriverTransportProviderRole.OWNER
        else:
            role_dialog = TransportProviderDriverRoleDialog(
                parent=self._window,
                driver_name=driver.name,
            )
            if role_dialog.result is None:
                messagebox.showinfo(
                    "Motorista cadastrado",
                    (
                        "O motorista foi cadastrado, mas ainda "
                        "não foi vinculado a este prestador."
                    ),
                    parent=self._window,
                )
                return
            role = role_dialog.result

        self._run_change(
            task=lambda: self._set_driver_affiliation_callback(
                driver_id=driver.driver_id,
                transport_provider_id=self._provider_id,
                role=role,
            ),
            success_message=(
                "Motorista cadastrado e vinculado ao prestador."
            ),
        )

    def _edit_driver(self) -> None:
        if self._is_loading or self._details is None:
            return

        selection = self.driver_tree.selection()
        if not selection:
            return

        driver_id = int(selection[0])
        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._get_driver_callback(
                driver_id
            ),
            on_success=self._open_driver_edit,
            on_error=self._show_error,
        )

    def _open_driver_edit(self, driver) -> None:
        self._set_loading(False)

        dialog = DriverEditDialog(
            parent=self._window,
            driver=driver,
            update_driver_callback=(
                self._update_driver_callback
            ),
        )

        if dialog.result is not None:
            self._load()

    def _link_driver(self) -> None:
        if self._is_loading or self._details is None:
            return

        provider = self._details.provider

        if (
            provider.provider_type
            == TransportProviderType.INDIVIDUAL
            and self._details.drivers
        ):
            messagebox.showinfo(
                "Motorista já vinculado",
                (
                    "Prestador pessoa física já possui "
                    "motorista vinculado."
                ),
                parent=self._window,
            )
            return

        dialog = TransportProviderDriverLinkDialog(
            parent=self._window,
            provider_name=(
                provider.trade_name
                or provider.legal_name
            ),
            list_drivers_callback=(
                self._list_drivers_callback
            ),
        )

        if dialog.result is None:
            return

        driver, role = dialog.result

        if (
            provider.provider_type
            == TransportProviderType.INDIVIDUAL
        ):
            role = DriverTransportProviderRole.OWNER

        if not messagebox.askyesno(
            "Vincular motorista",
            (
                f"Vincular {driver.name} ao prestador "
                f"{provider.trade_name or provider.legal_name}?\n\n"
                "Se o motorista possuir outro vínculo ativo, "
                "ele será encerrado e preservado no histórico."
            ),
            parent=self._window,
        ):
            return

        self._run_change(
            task=lambda: self._set_driver_affiliation_callback(
                driver_id=driver.driver_id,
                transport_provider_id=self._provider_id,
                role=role,
            ),
            success_message="Motorista vinculado ao prestador.",
        )

    def _link_vehicle(self) -> None:
        if self._is_loading or self._details is None:
            return

        provider = self._details.provider
        dialog = TransportProviderVehicleLinkDialog(
            parent=self._window,
            provider_name=(
                provider.trade_name
                or provider.legal_name
            ),
            search_vehicles_callback=(
                self._search_vehicles_callback
            ),
        )

        if dialog.result is None:
            return

        vehicle, relation = dialog.result

        if not messagebox.askyesno(
            "Vincular veículo",
            (
                f"Vincular o veículo {vehicle.plate} ao prestador "
                f"{provider.trade_name or provider.legal_name}?\n\n"
                "Se o veículo possuir outro vínculo ativo, "
                "ele será encerrado e preservado no histórico."
            ),
            parent=self._window,
        ):
            return

        self._run_change(
            task=lambda: self._set_vehicle_affiliation_callback(
                vehicle_id=vehicle.vehicle_id,
                transport_provider_id=self._provider_id,
                relation=relation,
            ),
            success_message="Veículo vinculado ao prestador.",
        )

    def _run_change(
        self,
        task,
        success_message: str,
    ) -> None:
        self._set_loading(True)
        self._task_runner.run(
            task=task,
            on_success=lambda _result: self._changed(
                success_message
            ),
            on_error=self._show_error,
        )

    def _changed(
        self,
        success_message: str,
    ) -> None:
        messagebox.showinfo(
            "Operação concluída",
            success_message,
            parent=self._window,
        )
        self._set_loading(False)
        self._load()

    def _show_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Operação não realizada",
            str(error),
            parent=self._window,
        )

    def _set_loading(self, value: bool) -> None:
        self._is_loading = value
        state = "disabled" if value else "normal"

        self.create_driver_button.configure(state=state)
        self.link_driver_button.configure(state=state)
        self.link_vehicle_button.configure(state=state)
        self.loading_label.configure(
            text=(
                "Atualizando..."
                if value
                else ""
            )
        )

        if value:
            self.edit_driver_button.configure(
                state="disabled"
            )
        else:
            self._on_driver_selection()

    def _on_driver_selection(
        self,
        _event=None,
    ) -> None:
        self.edit_driver_button.configure(
            state=(
                "normal"
                if (
                    self.driver_tree.selection()
                    and not self._is_loading
                )
                else "disabled"
            )
        )

    def _close(self) -> None:
        if self._is_loading:
            return
        self._window.destroy()
