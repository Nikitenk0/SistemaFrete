from tkinter import messagebox, ttk

import customtkinter as ctk

from application.dtos.freight_driver_selection import (
    FreightDriverSelectionItem,
)
from presentation.desktop.async_task_runner import (
    TkAsyncTaskRunner,
)
from presentation.desktop.freight_operational_inputs import (
    normalize_driver_search_query,
)


class FreightDriverDialog:

    def __init__(
        self,
        parent,
        unit_position: int,
        search_drivers_callback,
    ):
        self.result: FreightDriverSelectionItem | None = None
        self._search_drivers_callback = search_drivers_callback
        self._is_loading = False
        self._items_by_tree_id: dict[
            str,
            FreightDriverSelectionItem,
        ] = {}

        self._window = ctk.CTkToplevel(parent)
        self._window.title(
            f"Atribuir motorista - Unidade {unit_position}"
        )
        self._window.transient(parent.winfo_toplevel())
        self._window.grab_set()
        self._window.protocol(
            "WM_DELETE_WINDOW",
            self._cancel,
        )
        self._window.grid_columnconfigure(0, weight=1)
        self._window.grid_rowconfigure(2, weight=1)

        self._task_runner = TkAsyncTaskRunner(
            scheduler=self._window
        )

        ctk.CTkLabel(
            self._window,
            text=f"Unidade {unit_position}",
            font=("Arial", 16, "bold"),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=24,
            pady=(20, 8),
        )

        search_frame = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        search_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 10),
        )
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Nome, CPF, RG ou CNH",
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8),
        )
        self.search_entry.bind(
            "<Return>",
            lambda _event: self.search(),
        )

        self.search_button = ctk.CTkButton(
            search_frame,
            text="Pesquisar",
            width=100,
            command=self.search,
        )
        self.search_button.grid(
            row=0,
            column=1,
        )

        result_frame = ctk.CTkFrame(
            self._window,
        )
        result_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=24,
            pady=(0, 8),
        )
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        columns = (
            "id",
            "name",
            "cpf",
            "cnh",
            "category",
        )
        self.tree = ttk.Treeview(
            result_frame,
            columns=columns,
            show="headings",
            height=8,
        )
        headings = {
            "id": "ID",
            "name": "Motorista",
            "cpf": "CPF",
            "cnh": "CNH",
            "category": "Cat.",
        }
        widths = {
            "id": 55,
            "name": 230,
            "cpf": 120,
            "cnh": 120,
            "category": 55,
        }
        for column in columns:
            self.tree.heading(
                column,
                text=headings[column],
            )
            self.tree.column(
                column,
                width=widths[column],
                minwidth=45,
                anchor=(
                    "w"
                    if column == "name"
                    else "center"
                ),
            )

        scrollbar = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(
            yscrollcommand=scrollbar.set,
        )
        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        self.tree.bind(
            "<<TreeviewSelect>>",
            lambda _event: self._update_assign_state(),
        )
        self.tree.bind(
            "<Double-1>",
            lambda _event: self._assign(),
        )

        bottom = ctk.CTkFrame(
            self._window,
            fg_color="transparent",
        )
        bottom.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=24,
            pady=(0, 20),
        )
        bottom.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            bottom,
            text="Pesquise um motorista disponível.",
        )
        self.status_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.assign_button = ctk.CTkButton(
            bottom,
            text="Atribuir",
            width=100,
            state="disabled",
            command=self._assign,
        )
        self.assign_button.grid(
            row=0,
            column=1,
            padx=(8, 8),
        )

        ctk.CTkButton(
            bottom,
            text="Cancelar",
            width=100,
            command=self._cancel,
        ).grid(
            row=0,
            column=2,
        )

        self._window.update_idletasks()
        required_width = max(
            700,
            self._window.winfo_reqwidth() + 40,
        )
        required_height = max(
            430,
            self._window.winfo_reqheight() + 40,
        )
        self._window.minsize(680, 410)
        self._window.geometry(
            f"{required_width}x{required_height}"
        )

        self.search_entry.focus_set()
        self._window.wait_window()

    def search(self) -> None:
        if self._is_loading:
            return

        try:
            query = normalize_driver_search_query(
                self.search_entry.get()
            )
        except ValueError as error:
            messagebox.showwarning(
                "Pesquisa inválida",
                str(error),
                parent=self._window,
            )
            return

        self._set_loading(True)
        self._task_runner.run(
            task=lambda: self._search_drivers_callback(
                query=query,
                limit=20,
            ),
            on_success=self._on_search_success,
            on_error=self._on_search_error,
        )

    def _on_search_success(
        self,
        items: tuple[FreightDriverSelectionItem, ...],
    ) -> None:
        if not self._window_exists():
            return

        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        self._items_by_tree_id.clear()

        for item in items:
            tree_id = str(item.driver_id)
            self._items_by_tree_id[tree_id] = item
            self.tree.insert(
                "",
                "end",
                iid=tree_id,
                values=(
                    item.driver_id,
                    item.name,
                    self._format_cpf(item.cpf),
                    item.cnh_number,
                    item.cnh_category,
                ),
            )

        self.status_label.configure(
            text=(
                f"{len(items)} motorista(s) disponível(is)."
                if items
                else "Nenhum motorista disponível encontrado."
            )
        )
        self._set_loading(False)
        self._update_assign_state()

    def _on_search_error(
        self,
        error: Exception,
    ) -> None:
        if not self._window_exists():
            return

        self._set_loading(False)
        messagebox.showerror(
            "Erro",
            "Não foi possível pesquisar motoristas.\n\n"
            f"{error}",
            parent=self._window,
        )

    def _set_loading(
        self,
        value: bool,
    ) -> None:
        self._is_loading = value
        self.search_button.configure(
            state=(
                "disabled"
                if value
                else "normal"
            ),
            text=(
                "Pesquisando..."
                if value
                else "Pesquisar"
            ),
        )
        self.assign_button.configure(
            state="disabled"
        )
        if value:
            self.status_label.configure(
                text="Pesquisando motoristas..."
            )

    def _update_assign_state(self) -> None:
        if self._is_loading:
            return

        self.assign_button.configure(
            state=(
                "normal"
                if self.tree.selection()
                else "disabled"
            )
        )

    def _assign(self) -> None:
        if self._is_loading:
            return

        selection = self.tree.selection()
        if not selection:
            return

        item = self._items_by_tree_id.get(
            selection[0]
        )
        if item is None:
            return

        self.result = item
        self._close()

    def _cancel(self) -> None:
        self.result = None
        self._close()

    def _close(self) -> None:
        if self._window_exists():
            try:
                self._window.grab_release()
            except Exception:
                pass
            self._window.destroy()

    def _window_exists(self) -> bool:
        try:
            return bool(
                self._window.winfo_exists()
            )
        except Exception:
            return False

    @staticmethod
    def _format_cpf(cpf: str) -> str:
        digits = "".join(
            character
            for character in cpf
            if character.isdigit()
        )
        if len(digits) != 11:
            return cpf
        return (
            f"{digits[:3]}.{digits[3:6]}."
            f"{digits[6:9]}-{digits[9:]}"
        )
