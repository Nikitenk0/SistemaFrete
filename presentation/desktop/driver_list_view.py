from tkinter import messagebox, ttk

import customtkinter as ctk

from presentation.desktop.async_task_runner import TkAsyncTaskRunner
from presentation.desktop.driver_catalog_formatting import (
    DRIVER_STATUS_OPTIONS,
    driver_status_label,
    format_driver_cpf,
    format_driver_date,
    format_driver_phone,
)
from presentation.desktop.driver_create_dialog import DriverCreateDialog
from presentation.desktop.driver_edit_dialog import DriverEditDialog


class DriverListView:

    def __init__(
        self,
        parent,
        list_drivers_callback,
        get_driver_callback,
        create_driver_callback,
        update_driver_callback,
        navigate_back,
    ):
        self.parent = parent
        self._list_drivers_callback = list_drivers_callback
        self._get_driver_callback = get_driver_callback
        self._create_driver_callback = create_driver_callback
        self._update_driver_callback = update_driver_callback
        self._navigate_back = navigate_back
        self._is_loading = False
        self._task_runner = TkAsyncTaskRunner(scheduler=parent)

        self._build()
        self.search()

    def _build(self) -> None:
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )
        self.main_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=24,
            pady=18,
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self.main_frame,
            text="MOTORISTAS",
            font=("Arial", 22, "bold"),
        ).grid(row=0, column=0, pady=(0, 4))

        ctk.CTkLabel(
            self.main_frame,
            text=(
                "Consulte, cadastre e corrija os dados cadastrais "
                "dos motoristas."
            ),
            font=("Arial", 12),
        ).grid(row=1, column=0, pady=(0, 16))

        self._build_filters()
        self._build_actions()
        self._build_results()

    def _build_filters(self) -> None:
        frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        frame.grid(row=2, column=0, sticky="ew")
        frame.grid_columnconfigure(0, weight=3)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame,
            text="Nome, CPF, RG ou CNH",
        ).grid(row=0, column=0, pady=(0, 4))
        self.query_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Digite para pesquisar",
        )
        self.query_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 8),
        )
        self.query_entry.bind(
            "<Return>",
            lambda _event: self.search(),
        )

        ctk.CTkLabel(frame, text="Status").grid(
            row=0,
            column=1,
            pady=(0, 4),
        )
        self.status_combo = ctk.CTkComboBox(
            frame,
            values=list(DRIVER_STATUS_OPTIONS),
            state="readonly",
            width=145,
        )
        self.status_combo.grid(row=1, column=1, sticky="ew")
        self.status_combo.set("Todos")

    def _build_actions(self) -> None:
        frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        frame.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(14, 10),
        )

        self.search_button = ctk.CTkButton(
            frame,
            text="Pesquisar",
            width=105,
            command=self.search,
        )
        self.search_button.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame,
            text="Limpar filtros",
            width=115,
            command=self.clear_filters,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame,
            text="Novo motorista",
            width=125,
            command=self.create_driver,
        ).pack(side="left", padx=(0, 8))

        self.edit_button = ctk.CTkButton(
            frame,
            text="Editar cadastro",
            width=125,
            state="disabled",
            command=self.edit_selected_driver,
        )
        self.edit_button.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            frame,
            text="← Voltar",
            width=100,
            command=self._navigate_back,
        ).pack(side="right")

        self.result_count_label = ctk.CTkLabel(frame, text="")
        self.result_count_label.pack(side="right", padx=12)

    def _build_results(self) -> None:
        frame = ctk.CTkFrame(self.main_frame)
        frame.grid(row=4, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        columns = (
            "driver_id",
            "name",
            "cpf",
            "cnh",
            "category",
            "expiration",
            "status",
            "phone",
            "email",
        )
        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
        )

        headings = {
            "driver_id": "ID",
            "name": "Motorista",
            "cpf": "CPF",
            "cnh": "CNH",
            "category": "Cat.",
            "expiration": "Validade",
            "status": "Status",
            "phone": "Telefone",
            "email": "E-mail",
        }
        widths = {
            "driver_id": 55,
            "name": 190,
            "cpf": 115,
            "cnh": 115,
            "category": 55,
            "expiration": 90,
            "status": 80,
            "phone": 120,
            "email": 190,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                minwidth=50,
                anchor="w" if column in {"name", "email"} else "center",
            )

        vertical = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview,
        )
        horizontal = ttk.Scrollbar(
            frame,
            orient="horizontal",
            command=self.tree.xview,
        )
        self.tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_selection)
        self.tree.bind(
            "<Double-1>",
            lambda _event: self.edit_selected_driver(),
        )

    def search(self) -> None:
        if self._is_loading:
            return

        try:
            status = DRIVER_STATUS_OPTIONS[self.status_combo.get()]
        except KeyError:
            messagebox.showwarning(
                "Filtro inválido",
                "Status de motorista inválido.",
                parent=self.parent,
            )
            return

        query = self.query_entry.get().strip()
        self._set_loading(True)

        self._task_runner.run(
            task=lambda: self._list_drivers_callback(
                query=query,
                status=status,
                limit=200,
            ),
            on_success=self._show_results,
            on_error=self._show_error,
        )

    def _show_results(self, items) -> None:
        self._set_loading(False)
        self.tree.delete(*self.tree.get_children())

        for item in items:
            self.tree.insert(
                "",
                "end",
                iid=str(item.driver_id),
                values=(
                    item.driver_id,
                    item.name,
                    format_driver_cpf(item.cpf),
                    item.cnh_number,
                    item.cnh_category,
                    format_driver_date(item.cnh_expiration_date),
                    driver_status_label(item.status),
                    format_driver_phone(item.primary_phone),
                    item.primary_email or "--",
                ),
            )

        self.result_count_label.configure(
            text=f"{len(items)} resultado(s)"
        )
        self.edit_button.configure(state="disabled")

    def _show_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível consultar os motoristas.\n\n"
            f"{error}",
            parent=self.parent,
        )

    def clear_filters(self) -> None:
        self.query_entry.delete(0, "end")
        self.status_combo.set("Todos")
        self.search()

    def create_driver(self) -> None:
        dialog = DriverCreateDialog(
            parent=self.parent,
            create_driver_callback=self._create_driver_callback,
        )
        if dialog.result is not None:
            self.search()

    def edit_selected_driver(self) -> None:
        selection = self.tree.selection()
        if not selection or self._is_loading:
            return

        driver_id = int(selection[0])
        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._get_driver_callback(driver_id),
            on_success=self._open_edit_dialog,
            on_error=self._show_driver_load_error,
        )

    def _open_edit_dialog(self, driver) -> None:
        self._set_loading(False)
        dialog = DriverEditDialog(
            parent=self.parent,
            driver=driver,
            update_driver_callback=self._update_driver_callback,
        )
        if dialog.result is not None:
            self.search()

    def _show_driver_load_error(self, error: Exception) -> None:
        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível abrir o cadastro do motorista.\n\n"
            f"{error}",
            parent=self.parent,
        )

    def _set_loading(self, value: bool) -> None:
        self._is_loading = value
        self.search_button.configure(
            state="disabled" if value else "normal",
            text="Pesquisando..." if value else "Pesquisar",
        )
        if value:
            self.edit_button.configure(state="disabled")
        else:
            self._on_selection()

    def _on_selection(self, _event=None) -> None:
        state = (
            "normal"
            if self.tree.selection() and not self._is_loading
            else "disabled"
        )
        self.edit_button.configure(state=state)
