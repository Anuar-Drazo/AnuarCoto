import customtkinter as ctk

import anuarcoto_db
from componentes import COLOR_FONDO
from pantallas import JuegoFrame, LoginFrame, MenuFrame, RegistroFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo Mental")
        self.geometry("440x560")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO)

        self.usuario_actual = None
        self.configuracion_partida = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.pantallas = {}
        for clase in (LoginFrame, RegistroFrame, MenuFrame, JuegoFrame):
            pantalla = clase(self)
            self.pantallas[clase.__name__] = pantalla
            pantalla.grid(row=0, column=0, sticky="nsew")

        self.mostrar("LoginFrame")

    def mostrar(self, nombre):
        pantalla = self.pantallas[nombre]
        if hasattr(pantalla, "al_mostrar"):
            pantalla.al_mostrar()
        pantalla.tkraise()
        self.focus()

    def iniciar_sesion(self, usuario):
        self.usuario_actual = usuario
        self.mostrar("MenuFrame")

    def iniciar_juego(self, operacion, modo):
        self.configuracion_partida = {
            "operacion": operacion,
            "modo": modo,
        }
        self.mostrar("JuegoFrame")

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.configuracion_partida = None
        self.mostrar("LoginFrame")


if __name__ == "__main__":
    anuarcoto_db.inicializar()
    App().mainloop()
