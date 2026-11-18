import random
import sqlite3

import customtkinter as ctk

import anuarcoto_db

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_FONDO = "#f4f1fa"
COLOR_PRINCIPAL = "#6c4ab6"
COLOR_HOVER = "#573a96"
COLOR_TEXTO_SUAVE = "#6b6475"
COLOR_ERROR = "#c0392b"
COLOR_EXITO = "#218c54"

OPERACIONES = [
    "Suma de 2 digitos",
    "Resta de 2 digitos",
    "Multiplicacion (2 dig. × 1)",
    "Division exacta",
]

NUM_PREGUNTAS = 10
FUENTE = "Century Gothic"


def fuente(tamano=14, peso="normal"):
    return ctk.CTkFont(family=FUENTE, size=tamano, weight=peso)


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


class LoginFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        ctk.CTkLabel(
            self,
            text="Cálculo Mental",
            text_color=COLOR_PRINCIPAL,
            font=fuente(30, "bold"),
        ).pack(pady=(70, 5))
        ctk.CTkLabel(self, text="Inicia sesión para jugar", font=fuente(14)).pack(
            pady=(0, 30)
        )

        self.entry_usuario = ctk.CTkEntry(self, placeholder_text="Usuario", width=260, height=40, font=fuente())
        self.entry_usuario.pack(pady=8)
        self.entry_password = ctk.CTkEntry(
            self, placeholder_text="Contraseña", show="*", width=260, height=40,
            font=fuente(),
        )
        self.entry_password.pack(pady=8)
        self.entry_password.bind("<Return>", lambda _evento: self.entrar())

        self.mensaje = ctk.CTkLabel(self, text="", text_color=COLOR_ERROR, font=fuente())
        self.mensaje.pack(pady=(5, 0))

        ctk.CTkButton(
            self,
            text="Entrar",
            width=260,
            height=42,
            fg_color=COLOR_PRINCIPAL,
            hover_color=COLOR_HOVER,
            command=self.entrar,
            font=fuente(),
        ).pack(pady=(15, 8))
        ctk.CTkButton(
            self,
            text="Crear cuenta",
            width=260,
            height=42,
            fg_color="transparent",
            border_width=2,
            text_color=COLOR_PRINCIPAL,
            border_color=COLOR_PRINCIPAL,
            hover_color="#e6def5",
            command=lambda: app.mostrar("RegistroFrame"),
            font=fuente(),
        ).pack(pady=8)

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

        ctk.CTkLabel(
            self,
            text="Crear cuenta",
            text_color=COLOR_PRINCIPAL,
            font=fuente(28, "bold"),
        ).pack(pady=(60, 25))

        self.entry_usuario = ctk.CTkEntry(
            self, placeholder_text="Usuario (3-20 caracteres)", width=260, height=40,
            font=fuente(),
        )
        self.entry_usuario.pack(pady=8)
        self.entry_password = ctk.CTkEntry(
            self, placeholder_text="Contraseña (mín. 4)", show="*", width=260, height=40,
            font=fuente(),
        )
        self.entry_password.pack(pady=8)
        self.entry_confirmar = ctk.CTkEntry(
            self, placeholder_text="Confirmar contraseña", show="*", width=260, height=40,
            font=fuente(),
        )
        self.entry_confirmar.pack(pady=8)
        self.entry_confirmar.bind("<Return>", lambda _evento: self.registrar())

        self.mensaje = ctk.CTkLabel(self, text="", font=fuente())
        self.mensaje.pack(pady=(5, 0))

        ctk.CTkButton(
            self,
            text="Registrarme",
            width=260,
            height=42,
            fg_color=COLOR_PRINCIPAL,
            hover_color=COLOR_HOVER,
            command=self.registrar,
            font=fuente(),
        ).pack(pady=(15, 8))
        ctk.CTkButton(
            self,
            text="Volver",
            width=260,
            height=42,
            fg_color="transparent",
            border_width=2,
            text_color=COLOR_PRINCIPAL,
            border_color=COLOR_PRINCIPAL,
            hover_color="#e6def5",
            command=lambda: app.mostrar("LoginFrame"),
            font=fuente(),
        ).pack(pady=8)

    def al_mostrar(self):
        self.entry_usuario.delete(0, "end")
        self.entry_password.delete(0, "end")
        self.entry_confirmar.delete(0, "end")
        self.entry_usuario._activate_placeholder()
        self.entry_password._activate_placeholder()
        self.entry_confirmar._activate_placeholder()
        self.mensaje.configure(text="")

    def registrar(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        if password != self.entry_confirmar.get():
            self.mensaje.configure(text="Las contraseñas no coinciden.", text_color=COLOR_ERROR)
            return

        ok, texto = anuarcoto_db.registrar_usuario(usuario, password)
        if not ok:
            self.mensaje.configure(text=texto, text_color=COLOR_ERROR)
            return

        datos = anuarcoto_db.validar_login(usuario, password)
        if datos is None:
            self.mensaje.configure(
                text="La cuenta se creó, pero no se pudo iniciar sesión.", text_color=COLOR_ERROR
            )
            return
        self.app.iniciar_sesion(datos)


class MenuFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        self.saludo = ctk.CTkLabel(
            self, text="", text_color=COLOR_PRINCIPAL, font=fuente(24, "bold")
        )
        self.saludo.pack(pady=(35, 5))

        ctk.CTkLabel(self, text="Modo", font=fuente()).pack(pady=(12, 3))
        self.modo = ctk.CTkSegmentedButton(
            self,
            values=["Práctica", "Competencia"],
            selected_color=COLOR_PRINCIPAL,
            selected_hover_color=COLOR_HOVER,
            font=fuente(),
        )
        self.modo.set("Práctica")
        self.modo.pack()

        ctk.CTkLabel(self, text="¿Qué quieres practicar?", font=fuente()).pack(pady=(20, 8))

        self.botones_operaciones = []
        for indice, nombre in enumerate(OPERACIONES):
            disponible = indice == 0
            texto = nombre if disponible else f"{nombre} (próximamente)"
            boton = ctk.CTkButton(
                self,
                text=texto,
                width=300,
                height=42,
                fg_color=COLOR_PRINCIPAL if disponible else "#c9c2d4",
                hover_color=COLOR_HOVER if disponible else "#c9c2d4",
                text_color="white" if disponible else "#f7f6f9",
                state="normal" if disponible else "disabled",
                command=lambda i=indice: self.elegir(i),
                font=fuente(),
            )
            boton.pack(pady=4)
            self.botones_operaciones.append(boton)

        self.aviso = ctk.CTkLabel(self, text="", text_color=COLOR_TEXTO_SUAVE, font=fuente())
        self.aviso.pack(pady=(6, 0))

        ctk.CTkButton(
            self,
            text="Cerrar sesión",
            width=280,
            height=36,
            fg_color="transparent",
            border_width=2,
            text_color=COLOR_PRINCIPAL,
            border_color=COLOR_PRINCIPAL,
            hover_color="#e6def5",
            command=app.cerrar_sesion,
            font=fuente(),
        ).pack(pady=(12, 0))

    def al_mostrar(self):
        nombre = self.app.usuario_actual["nombre"]
        self.saludo.configure(text=f"¡Hola, {nombre}!")
        self.aviso.configure(text="")

    def elegir(self, indice):
        if indice != 0:
            self.aviso.configure(text="Esta operación estará disponible próximamente.")
            return
        self.app.iniciar_juego(OPERACIONES[indice], self.modo.get())


class JuegoFrame(ctk.CTkFrame):
    """Pantalla reutilizable para los ejercicios de las distintas operaciones."""

    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app
        self.estado = "pregunta"
        self.numero_pregunta = 0
        self.puntaje = 0
        self.numero_a = 0
        self.numero_b = 0
        self.respuesta_correcta = 0

        self.titulo = ctk.CTkLabel(
            self, text="", text_color=COLOR_PRINCIPAL, font=fuente(25, "bold")
        )
        self.titulo.pack(pady=(38, 4))

        self.etiqueta_modo = ctk.CTkLabel(self, text="", text_color=COLOR_TEXTO_SUAVE, font=fuente())
        self.etiqueta_modo.pack(pady=(0, 18))

        self.progreso = ctk.CTkLabel(self, text="", font=fuente(14, "bold"))
        self.progreso.pack(pady=5)

        self.problema = ctk.CTkLabel(
            self, text="", font=fuente(38, "bold"), text_color=COLOR_PRINCIPAL
        )
        self.problema.pack(pady=(25, 20))

        self.instruccion = ctk.CTkLabel(self, text="Escribe el resultado de la suma.", font=fuente())
        self.instruccion.pack(pady=(0, 10))

        self.entry_respuesta = ctk.CTkEntry(
            self, placeholder_text="Tu respuesta", width=220, height=44, justify="center",
            font=fuente(),
        )
        self.entry_respuesta.pack(pady=8)
        self.entry_respuesta.bind("<Return>", lambda _evento: self.accion_principal())

        self.mensaje = ctk.CTkLabel(self, text="", font=fuente(14))
        self.mensaje.pack(pady=(8, 12))

        self.boton_principal = ctk.CTkButton(
            self,
            text="Comprobar",
            width=220,
            height=42,
            fg_color=COLOR_PRINCIPAL,
            hover_color=COLOR_HOVER,
            command=self.accion_principal,
            font=fuente(),
        )
        self.boton_principal.pack(pady=6)

        ctk.CTkButton(
            self,
            text="Volver al menú",
            width=220,
            height=38,
            fg_color="transparent",
            border_width=2,
            text_color=COLOR_PRINCIPAL,
            border_color=COLOR_PRINCIPAL,
            hover_color="#e6def5",
            command=lambda: app.mostrar("MenuFrame"),
            font=fuente(),
        ).pack(pady=8)

    def al_mostrar(self):
        configuracion = self.app.configuracion_partida
        if not configuracion or not self.app.usuario_actual:
            self.app.mostrar("MenuFrame")
            return

        self.operacion = configuracion["operacion"]
        self.modo = configuracion["modo"]
        self.titulo.configure(text=self.operacion)
        self.etiqueta_modo.configure(text=f"Modo: {self.modo}")
        self.iniciar_partida()

    def iniciar_partida(self):
        self.numero_pregunta = 0
        self.puntaje = 0
        self.estado = "pregunta"
        self.mensaje.configure(text="", text_color=COLOR_TEXTO_SUAVE)
        self.instruccion.configure(text="Escribe el resultado de la suma.")
        self.entry_respuesta.configure(state="normal")
        self.boton_principal.configure(text="Comprobar")
        self.mostrar_siguiente_pregunta()

    def mostrar_siguiente_pregunta(self):
        self.numero_pregunta += 1
        self.numero_a = random.randint(10, 99)
        self.numero_b = random.randint(10, 99)
        self.respuesta_correcta = self.numero_a + self.numero_b

        self.progreso.configure(
            text=f"Pregunta {self.numero_pregunta} de {NUM_PREGUNTAS}    |    Puntos: {self.puntaje}"
        )
        self.problema.configure(text=f"{self.numero_a} + {self.numero_b} = ?")
        self.entry_respuesta.configure(state="normal")
        self.entry_respuesta.delete(0, "end")
        self.mensaje.configure(text="", text_color=COLOR_TEXTO_SUAVE)
        self.estado = "pregunta"
        self.boton_principal.configure(text="Comprobar")

    def accion_principal(self):
        if self.estado == "pregunta":
            self.comprobar_respuesta()
        elif self.estado == "respondida":
            if self.numero_pregunta < NUM_PREGUNTAS:
                self.mostrar_siguiente_pregunta()
            else:
                self.finalizar_partida()
        elif self.estado == "finalizada":
            self.iniciar_partida()

    def comprobar_respuesta(self):
        texto = self.entry_respuesta.get().strip()
        if not texto:
            self.mensaje.configure(
                text="Primero escribe una respuesta.", text_color=COLOR_ERROR
            )
            return

        try:
            respuesta = int(texto)
        except ValueError:
            self.mensaje.configure(
                text="La respuesta debe ser un número entero.", text_color=COLOR_ERROR
            )
            return

        self.estado = "respondida"
        self.entry_respuesta.configure(state="disabled")

        if respuesta == self.respuesta_correcta:
            self.puntaje += 1
            self.mensaje.configure(text="¡Correcto! Muy bien.", text_color=COLOR_EXITO)
        else:
            self.mensaje.configure(
                text=f"No es correcto. La respuesta era {self.respuesta_correcta}.",
                text_color=COLOR_ERROR,
            )

        self.progreso.configure(
            text=f"Pregunta {self.numero_pregunta} de {NUM_PREGUNTAS}    |    Puntos: {self.puntaje}"
        )
        siguiente_texto = "Siguiente pregunta" if self.numero_pregunta < NUM_PREGUNTAS else "Ver resultado"
        self.boton_principal.configure(text=siguiente_texto)

    def finalizar_partida(self):
        self.estado = "finalizada"
        self.progreso.configure(text="Partida terminada")
        self.problema.configure(text=f"{self.puntaje} / {NUM_PREGUNTAS}")
        porcentaje = round((self.puntaje / NUM_PREGUNTAS) * 100)
        self.instruccion.configure(text=f"Tu resultado: {porcentaje}% de respuestas correctas.")
        self.entry_respuesta.configure(state="disabled")

        try:
            anuarcoto_db.guardar_partida(
                self.app.usuario_actual["id"],
                self.operacion,
                self.modo,
                self.puntaje,
            )
            texto_guardado = "Tu resultado se guardó correctamente."
            color_guardado = COLOR_EXITO
        except sqlite3.Error:
            texto_guardado = "No se pudo guardar el resultado en la base de datos."
            color_guardado = COLOR_ERROR

        self.mensaje.configure(text=texto_guardado, text_color=color_guardado)
        self.boton_principal.configure(text="Jugar otra vez")


if __name__ == "__main__":
    anuarcoto_db.inicializar()
    App().mainloop()
