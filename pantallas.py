"""Pantallas de la aplicación: acceso, registro, menú y juego."""

import sqlite3

import customtkinter as ctk

import anuarcoto_db
from componentes import (
    COLOR_ERROR,
    COLOR_EXITO,
    COLOR_FONDO,
    COLOR_HOVER,
    COLOR_PRINCIPAL,
    COLOR_TEXTO_SUAVE,
    NUM_PREGUNTAS,
    crear_boton,
    crear_entrada,
    crear_etiqueta,
    fuente,
    limpiar_entradas,
)
from logica_juegos import (
    OPERACIONES,
    comprobar_respuesta,
    generar_ejercicio,
    obtener_instruccion,
)


class LoginFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        crear_etiqueta(
            self, "Cálculo Mental", color=COLOR_PRINCIPAL, tamano=30, peso="bold"
        ).pack(pady=(70, 5))
        crear_etiqueta(self, "Inicia sesión para jugar").pack(pady=(0, 30))

        self.entry_usuario = crear_entrada(self, "Usuario")
        self.entry_usuario.pack(pady=8)
        self.entry_password = crear_entrada(self, "Contraseña", password=True)
        self.entry_password.pack(pady=8)
        self.entry_password.bind("<Return>", lambda _evento: self.entrar())

        self.mensaje = crear_etiqueta(self, color=COLOR_ERROR)
        self.mensaje.pack(pady=(5, 0))

        crear_boton(self, "Entrar", self.entrar).pack(pady=(15, 8))
        crear_boton(
            self,
            "Crear cuenta",
            lambda: app.mostrar("RegistroFrame"),
            estilo="secundario",
        ).pack(pady=8)

    def al_mostrar(self):
        limpiar_entradas(self.entry_usuario, self.entry_password)
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

        crear_etiqueta(
            self, "Crear cuenta", color=COLOR_PRINCIPAL, tamano=28, peso="bold"
        ).pack(pady=(60, 25))

        self.entry_usuario = crear_entrada(self, "Usuario (3-20 caracteres)")
        self.entry_usuario.pack(pady=8)
        self.entry_password = crear_entrada(
            self, "Contraseña (mín. 4)", password=True
        )
        self.entry_password.pack(pady=8)
        self.entry_confirmar = crear_entrada(
            self, "Confirmar contraseña", password=True
        )
        self.entry_confirmar.pack(pady=8)
        self.entry_confirmar.bind("<Return>", lambda _evento: self.registrar())

        self.mensaje = crear_etiqueta(self)
        self.mensaje.pack(pady=(5, 0))

        crear_boton(self, "Registrarme", self.registrar).pack(pady=(15, 8))
        crear_boton(
            self,
            "Volver",
            lambda: app.mostrar("LoginFrame"),
            estilo="secundario",
        ).pack(pady=8)

    def al_mostrar(self):
        limpiar_entradas(
            self.entry_usuario,
            self.entry_password,
            self.entry_confirmar,
        )
        self.mensaje.configure(text="")

    def registrar(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        if password != self.entry_confirmar.get():
            self.mensaje.configure(
                text="Las contraseñas no coinciden.", text_color=COLOR_ERROR
            )
            return

        ok, texto = anuarcoto_db.registrar_usuario(usuario, password)
        if not ok:
            self.mensaje.configure(text=texto, text_color=COLOR_ERROR)
            return

        datos = anuarcoto_db.validar_login(usuario, password)
        if datos is None:
            self.mensaje.configure(
                text="La cuenta se creó, pero no se pudo iniciar sesión.",
                text_color=COLOR_ERROR,
            )
            return
        self.app.iniciar_sesion(datos)


class MenuFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        self.saludo = crear_etiqueta(
            self, color=COLOR_PRINCIPAL, tamano=24, peso="bold"
        )
        self.saludo.pack(pady=(35, 5))

        crear_etiqueta(self, "Modo").pack(pady=(12, 3))
        self.modo = ctk.CTkSegmentedButton(
            self,
            values=["Práctica", "Competencia"],
            selected_color=COLOR_PRINCIPAL,
            selected_hover_color=COLOR_HOVER,
            font=fuente(),
        )
        self.modo.set("Práctica")
        self.modo.pack()

        crear_etiqueta(self, "¿Qué quieres practicar?").pack(pady=(20, 8))

        self.botones_operaciones = []
        for indice, nombre in enumerate(OPERACIONES):
            boton = crear_boton(
                self,
                nombre,
                lambda i=indice: self.elegir(i),
                estilo="principal",
                width=300,
                height=42,
            )
            boton.pack(pady=4)
            self.botones_operaciones.append(boton)

        self.aviso = crear_etiqueta(self, color=COLOR_TEXTO_SUAVE)
        self.aviso.pack(pady=(6, 0))

        crear_boton(
            self,
            "Cerrar sesión",
            app.cerrar_sesion,
            estilo="secundario",
            width=280,
            height=36,
        ).pack(pady=(12, 0))

    def al_mostrar(self):
        nombre = self.app.usuario_actual["nombre"]
        self.saludo.configure(text=f"¡Hola, {nombre}!")
        self.aviso.configure(text="")

    def elegir(self, indice):
        self.app.iniciar_juego(OPERACIONES[indice], self.modo.get())


class JuegoFrame(ctk.CTkFrame):
    """Pantalla reutilizable para los ejercicios de las distintas operaciones."""

    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app
        self.estado = "pregunta"
        self.numero_pregunta = 0
        self.puntaje = 0
        self.ejercicio = None
        self.respuesta_correcta = 0

        self.titulo = crear_etiqueta(
            self, color=COLOR_PRINCIPAL, tamano=25, peso="bold"
        )
        self.titulo.pack(pady=(38, 4))

        self.etiqueta_modo = crear_etiqueta(self, color=COLOR_TEXTO_SUAVE)
        self.etiqueta_modo.pack(pady=(0, 18))

        self.progreso = crear_etiqueta(self, tamano=14, peso="bold")
        self.progreso.pack(pady=5)

        self.problema = crear_etiqueta(
            self, color=COLOR_PRINCIPAL, tamano=38, peso="bold"
        )
        self.problema.pack(pady=(25, 20))

        self.instruccion = crear_etiqueta(
            self, "Escribe el resultado de la operación."
        )
        self.instruccion.pack(pady=(0, 10))

        self.entry_respuesta = crear_entrada(
            self,
            "Tu respuesta",
            width=220,
            height=44,
            justify="center",
        )
        self.entry_respuesta.pack(pady=8)
        self.entry_respuesta.bind(
            "<Return>", lambda _evento: self.accion_principal()
        )

        self.mensaje = crear_etiqueta(self, tamano=14)
        self.mensaje.pack(pady=(8, 12))

        self.boton_principal = crear_boton(
            self,
            "Comprobar",
            self.accion_principal,
            width=220,
            height=42,
        )
        self.boton_principal.pack(pady=6)

        crear_boton(
            self,
            "Volver al menú",
            lambda: app.mostrar("MenuFrame"),
            estilo="secundario",
            width=220,
            height=38,
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
        self.instruccion.configure(text=obtener_instruccion(self.operacion))
        self.entry_respuesta.configure(state="normal")
        self.boton_principal.configure(text="Comprobar")
        self.mostrar_siguiente_pregunta()

    def mostrar_siguiente_pregunta(self):
        self.numero_pregunta += 1
        self.ejercicio = generar_ejercicio(self.operacion)
        self.respuesta_correcta = self.ejercicio.respuesta_correcta

        self._actualizar_progreso()
        self.problema.configure(text=self.ejercicio.expresion)
        self.entry_respuesta.configure(state="normal")
        self.entry_respuesta.delete(0, "end")
        self.mensaje.configure(text="", text_color=COLOR_TEXTO_SUAVE)
        self.estado = "pregunta"
        self.boton_principal.configure(text="Comprobar")

    def _actualizar_progreso(self):
        self.progreso.configure(
            text=(
                f"Pregunta {self.numero_pregunta} de {NUM_PREGUNTAS}"
                f"    |    Puntos: {self.puntaje}"
            )
        )

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
                text="La respuesta debe ser un número entero.",
                text_color=COLOR_ERROR,
            )
            return

        self.estado = "respondida"
        self.entry_respuesta.configure(state="disabled")

        if comprobar_respuesta(respuesta, self.ejercicio):
            self.puntaje += 1
            self.mensaje.configure(
                text="¡Correcto! Muy bien.", text_color=COLOR_EXITO
            )
        else:
            self.mensaje.configure(
                text=f"No es correcto. La respuesta era {self.respuesta_correcta}.",
                text_color=COLOR_ERROR,
            )

        self._actualizar_progreso()
        siguiente_texto = (
            "Siguiente pregunta"
            if self.numero_pregunta < NUM_PREGUNTAS
            else "Ver resultado"
        )
        self.boton_principal.configure(text=siguiente_texto)

    def finalizar_partida(self):
        self.estado = "finalizada"
        self.progreso.configure(text="Partida terminada")
        self.problema.configure(text=f"{self.puntaje} / {NUM_PREGUNTAS}")
        porcentaje = round((self.puntaje / NUM_PREGUNTAS) * 100)
        self.instruccion.configure(
            text=f"Tu resultado: {porcentaje}% de respuestas correctas."
        )
        self.entry_respuesta.configure(state="disabled")

        if self.modo == "Competencia":
            self._guardar_resultado_competencia()
        else:
            self.mensaje.configure(
                text="Resultado de práctica: no se guardó.",
                text_color=COLOR_TEXTO_SUAVE,
            )
        self.boton_principal.configure(text="Jugar otra vez")

    def _guardar_resultado_competencia(self):
        """Guarda únicamente las partidas competitivas."""
        try:
            anuarcoto_db.guardar_partida(
                self.app.usuario_actual["id"],
                self.operacion,
                self.modo,
                self.puntaje,
            )
        except sqlite3.Error:
            texto = "No se pudo guardar el resultado en la base de datos."
            color = COLOR_ERROR
        else:
            texto = "Tu resultado se guardó correctamente."
            color = COLOR_EXITO
        self.mensaje.configure(text=texto, text_color=color)
