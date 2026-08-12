import customtkinter as ctk
from telas.menu_principal import MenuPrincipal
from services.qualp.qualp import QualP


ctk.set_appearance_mode("light")     # ou "dark"
ctk.set_default_color_theme("blue")

janela = ctk.CTk()

app = MenuPrincipal(janela)

janela.mainloop()