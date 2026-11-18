import customtkinter as ctk

import anuarcoto_db

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_FONDO = "#f4f1fa"
COLOR_PRINCIPAL = "#6c4ab6"
COLOR_HOVER = "#573a96"

OPERACIONES = [
    "Suma de 2 dígitos",
    "Resta de 2 dígitos",
    "Multiplicación (2 dígitos × 1)",
    "División exacta",
]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo Mental")
        self.geometry("440x560")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO)

        self.usuario_actual = None


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.pantallas = {}
        for clase in (LoginFrame, RegistroFrame, MenuFrame):
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

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.mostrar("LoginFrame")


class LoginFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        ctk.CTkLabel(self, text="Cálculo Mental", text_color=COLOR_PRINCIPAL,
                     font=ctk.CTkFont(size=30, weight="bold")).pack(pady=(70, 5))
        ctk.CTkLabel(self, text="Inicia sesión para jugar",
                     font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        self.entry_usuario = ctk.CTkEntry(self, placeholder_text="Usuario", width=260, height=40)
        self.entry_usuario.pack(pady=8)
        self.entry_password = ctk.CTkEntry(self, placeholder_text="Contraseña",
                                           show="*", width=260, height=40)
        self.entry_password.pack(pady=8)
        self.entry_password.bind("<Return>", lambda e: self.entrar())

        self.mensaje = ctk.CTkLabel(self, text="", text_color="#c0392b")
        self.mensaje.pack(pady=(5, 0))

        ctk.CTkButton(self, text="Entrar", width=260, height=42, fg_color=COLOR_PRINCIPAL,
                      hover_color=COLOR_HOVER, command=self.entrar).pack(pady=(15, 8))
        ctk.CTkButton(self, text="Crear cuenta", width=260, height=42, fg_color="transparent",
                      border_width=2, text_color=COLOR_PRINCIPAL, border_color=COLOR_PRINCIPAL,
                      hover_color="#e6def5",
                      command=lambda: app.mostrar("RegistroFrame")).pack(pady=8)

    def al_mostrar(self):
        self.entry_usuario.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.entry_usuario._activate_placeholder()
        self.entry_password._activate_placeholder()
        self.mensaje.configure(text="")

    def entrar(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        if not usuario.strip() or not password:
            self.mensaje.configure(text="Escribe tu usuario y contraseña.")
            return
        datos = anuarcoto_db.validar_login(usuario, password)
        if datos is None:
            self.mensaje.configure(text="Usuario o contraseña incorrectos.")
            return
        self.app.iniciar_sesion(datos)


class RegistroFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        ctk.CTkLabel(self, text="Crear cuenta", text_color=COLOR_PRINCIPAL,
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(60, 25))

        self.entry_usuario = ctk.CTkEntry(self, placeholder_text="Usuario (3-20 caracteres)",
                                          width=260, height=40)
        self.entry_usuario.pack(pady=8)
        self.entry_password = ctk.CTkEntry(self, placeholder_text="Contraseña (mín. 4)",
                                           show="*", width=260, height=40)
        self.entry_password.pack(pady=8)
        self.entry_confirmar = ctk.CTkEntry(self, placeholder_text="Confirmar contraseña",
                                            show="*", width=260, height=40)
        self.entry_confirmar.pack(pady=8)
        self.entry_confirmar.bind("<Return>", lambda e: self.registrar())

        self.mensaje = ctk.CTkLabel(self, text="")
        self.mensaje.pack(pady=(5, 0))

        ctk.CTkButton(self, text="Registrarme", width=260, height=42, fg_color=COLOR_PRINCIPAL,
                      hover_color=COLOR_HOVER, command=self.registrar).pack(pady=(15, 8))
        ctk.CTkButton(self, text="Volver", width=260, height=42, fg_color="transparent",
                      border_width=2, text_color=COLOR_PRINCIPAL, border_color=COLOR_PRINCIPAL,
                      hover_color="#e6def5",
                      command=lambda: app.mostrar("LoginFrame")).pack(pady=8)

    def al_mostrar(self):
        for entry in (self.entry_usuario, self.entry_password, self.entry_confirmar):
            entry.delete(0, "end")
            entry._activate_placeholder()
        self.mensaje.configure(text="")

    def registrar(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        if password != self.entry_confirmar.get():
            self.mensaje.configure(text="Las contraseñas no coinciden.", text_color="#c0392b")
            return
        ok, texto = anuarcoto_db.registrar_usuario(usuario, password)
        if not ok:
            self.mensaje.configure(text=texto, text_color="#c0392b")
            return
        self.app.iniciar_sesion(anuarcoto_db.validar_login(usuario, password))


class MenuFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        self.saludo = ctk.CTkLabel(self, text="", text_color=COLOR_PRINCIPAL,
                                   font=ctk.CTkFont(size=24, weight="bold"))
        self.saludo.pack(pady=(40, 5))

        ctk.CTkLabel(self, text="Modo").pack(pady=(15, 3))
        self.modo = ctk.CTkSegmentedButton(self, values=["Práctica", "Competencia"],
                                           selected_color=COLOR_PRINCIPAL,
                                           selected_hover_color=COLOR_HOVER)
        self.modo.set("Práctica")
        self.modo.pack()

        ctk.CTkLabel(self, text="¿Qué quieres practicar?").pack(pady=(25, 8))
        for i, nombre in enumerate(OPERACIONES):
            ctk.CTkButton(self, text=nombre, width=280, height=44, fg_color=COLOR_PRINCIPAL,
                          hover_color=COLOR_HOVER,
                          command=lambda i=i: self.elegir(i)).pack(pady=5)

        self.aviso = ctk.CTkLabel(self, text="")
        self.aviso.pack(pady=(10, 0))

        ctk.CTkButton(self, text="Cerrar sesión", width=280, height=38, fg_color="transparent",
                      border_width=2, text_color=COLOR_PRINCIPAL, border_color=COLOR_PRINCIPAL,
                      hover_color="#e6def5", command=app.cerrar_sesion).pack(pady=(20, 0))

    def al_mostrar(self):
        self.saludo.configure(text=f"¡Hola, {self.app.usuario_actual['nombre']}!")
        self.aviso.configure(text="")

    def elegir(self, indice):
        self.aviso.configure(
            text=f"{OPERACIONES[indice]} - {self.modo.get()} (próximamente)")


if __name__ == "__main__":
    anuarcoto_db.inicializar()
    App().mainloop()