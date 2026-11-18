import sqlite3
import time
import tkinter as tk

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
    TemporizadorCircular,
    crear_boton,
    crear_entrada,
    crear_etiqueta,
    fuente,
    limpiar_entradas,
)
from logica_juegos import (
    DURACION_COMPETENCIA_SEGUNDOS,
    OPERACIONES,
    comprobar_respuesta,
    generar_ejercicio,
    obtener_instruccion,
)

MODOS_MENU = ["Práctica", "Competencia", "Ranking"]
FILTROS_OPERACION = ["Todas las operaciones", *OPERACIONES]


def crear_selector_modo(parent, seleccionado, comando):
    selector = ctk.CTkSegmentedButton(
        parent,
        values=MODOS_MENU,
        selected_color=COLOR_PRINCIPAL,
        selected_hover_color=COLOR_HOVER,
        font=fuente(11),
        command=comando,
    )
    selector.set(seleccionado)
    selector.pack(pady=(0, 2))
    return selector


class LoginFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        crear_etiqueta(
            self, "Cálculo Mental", color=COLOR_PRINCIPAL, tamaño=30, peso="bold"
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
            self, "Crear cuenta", color=COLOR_PRINCIPAL, tamaño=28, peso="bold"
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
            self, color=COLOR_PRINCIPAL, tamaño=24, peso="bold"
        )
        self.saludo.pack(pady=(35, 5))

        crear_etiqueta(self, "Modo").pack(pady=(12, 3))
        self.modo = crear_selector_modo(
            self, self.app.modo_actual, self.cambiar_modo
        )

        self.info_competencia = crear_etiqueta(
            self,
            "En Competencia: 3 intentos diarios entre las 4 operaciones · "
            "100 s por intento · cada error resta 1 punto. Solo tu mejor intento "
            "cuenta para el ranking.",
            color=COLOR_TEXTO_SUAVE,
            tamaño=10,
            justify="center",
            wraplength=365,
        )
        self.info_competencia.pack(pady=(1, 4))
        self.info_competencia.pack_forget()

        self.etiqueta_operaciones = crear_etiqueta(
            self, "¿Qué quieres practicar?"
        )
        self.etiqueta_operaciones.pack(pady=(20, 8))

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
        self.modo.set(self.app.modo_actual)
        self._actualizar_info_competencia()

    def cambiar_modo(self, modo):
        if modo == "Ranking":
            self.app.mostrar("RankingFrame")
            return
        self.app.modo_actual = modo
        self._actualizar_info_competencia()
        self.aviso.configure(text="")

    def _actualizar_info_competencia(self):
        if self.app.modo_actual == "Competencia":
            self.info_competencia.pack(
                before=self.etiqueta_operaciones,
                pady=(1, 4),
            )
            self.etiqueta_operaciones.pack_configure(pady=(8, 5))
        else:
            self.info_competencia.pack_forget()
            self.etiqueta_operaciones.pack_configure(pady=(20, 8))

    def elegir(self, indice):
        modo = self.app.modo_actual
        if modo == "Competencia" and not anuarcoto_db.puede_iniciar_competencia(
            self.app.usuario_actual["id"]
        ):
            self.aviso.configure(
                text="Ya utilizaste tus 3 intentos de hoy.",
                text_color=COLOR_ERROR,
            )
            return
        self.app.iniciar_juego(OPERACIONES[indice], modo)


class RankingFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app

        crear_etiqueta(
            self,
            "Ranking",
            color=COLOR_PRINCIPAL,
            tamaño=25,
            peso="bold",
        ).pack(pady=(14, 3))

        self.selector_modo = crear_selector_modo(
            self, "Ranking", self.cambiar_modo
        )

        crear_etiqueta(
            self,
            "Cada jugador aparece con su mejor intento. Aciertos/s = aciertos ÷ "
            "segundos; puntaje = aciertos − errores.",
            color=COLOR_TEXTO_SUAVE,
            tamaño=10,
            wraplength=380,
            justify="center",
        ).pack(pady=(3, 8))

        self.filtro_operacion = ctk.CTkOptionMenu(
            self,
            values=FILTROS_OPERACION,
            command=self.actualizar_ranking,
            font=fuente(11),
            dropdown_font=fuente(11),
            fg_color=COLOR_PRINCIPAL,
            button_color=COLOR_HOVER,
            button_hover_color=COLOR_HOVER,
        )
        self.filtro_operacion.set(FILTROS_OPERACION[0])
        self.filtro_operacion.pack(pady=(0, 7))

        self.contenedor_ranking = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.contenedor_ranking.pack(
            fill="both", expand=True, padx=14, pady=(0, 5)
        )

        crear_boton(
            self,
            "Volver al menú",
            lambda: self._volver_a_menu(self.app.modo_actual),
            estilo="secundario",
            width=220,
            height=36,
        ).pack(pady=(3, 10))

    def al_mostrar(self):
        self.selector_modo.set("Ranking")
        self.actualizar_ranking()

    def cambiar_modo(self, modo):
        if modo == "Ranking":
            return
        self._volver_a_menu(modo)

    def _volver_a_menu(self, modo):
        self.app.modo_actual = modo
        self.app.mostrar("MenuFrame")

    def actualizar_ranking(self, _seleccion=None):
        for widget in self.contenedor_ranking.winfo_children():
            widget.destroy()

        seleccion = self.filtro_operacion.get()
        operacion = None if seleccion == FILTROS_OPERACION[0] else seleccion

        try:
            ranking_ritmo = anuarcoto_db.obtener_ranking_competencia(
                operacion=operacion,
                criterio="ritmo",
                limite=10,
            )
            ranking_puntaje = anuarcoto_db.obtener_ranking_competencia(
                operacion=operacion,
                criterio="puntaje",
                limite=10,
            )
        except sqlite3.Error:
            crear_etiqueta(
                self.contenedor_ranking,
                "No se pudo cargar el ranking. Inténtalo de nuevo.",
                color=COLOR_ERROR,
                tamaño=12,
                wraplength=350,
            ).pack(pady=20)
            return

        self._crear_seccion(
            "Aciertos por segundo",
            "Mayor rapidez de aciertos, medida sobre el mejor intento.",
            ranking_ritmo,
            criterio="ritmo",
        )
        self._crear_seccion(
            "Puntaje general",
            "Cada acierto suma 1 punto y cada error resta 1.",
            ranking_puntaje,
            criterio="puntaje",
        )

    def _crear_seccion(self, titulo, descripcion, resultados, criterio):
        panel = ctk.CTkFrame(
            self.contenedor_ranking,
            fg_color="#ffffff",
            corner_radius=12,
        )
        panel.pack(fill="x", pady=5)

        crear_etiqueta(
            panel,
            titulo,
            color=COLOR_PRINCIPAL,
            tamaño=15,
            peso="bold",
        ).pack(anchor="w", padx=12, pady=(9, 0))
        crear_etiqueta(
            panel,
            descripcion,
            color=COLOR_TEXTO_SUAVE,
            tamaño=9,
            wraplength=350,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(0, 5))

        if not resultados:
            crear_etiqueta(
                panel,
                "Aún no hay resultados completos con el sistema actual de puntuación.",
                color=COLOR_TEXTO_SUAVE,
                tamaño=11,
            ).pack(anchor="w", padx=12, pady=(5, 12))
            return

        for posicion, resultado in enumerate(resultados, start=1):
            fila = ctk.CTkFrame(panel, fg_color="#f4f1fa", corner_radius=8)
            fila.pack(fill="x", padx=8, pady=3)

            cabecera = ctk.CTkFrame(fila, fg_color="transparent")
            cabecera.pack(fill="x", padx=8, pady=(5, 0))
            crear_etiqueta(
                cabecera,
                f"{posicion}. {resultado['nombre']}",
                tamaño=11,
                peso="bold",
            ).pack(side="left", anchor="w", fill="x", expand=True)

            if criterio == "ritmo":
                valor = f"{resultado['aciertos_por_segundo']:.3f} aciertos/s"
            else:
                valor = f"{resultado['puntaje']:+d} pts"
            crear_etiqueta(
                cabecera,
                valor,
                color=COLOR_PRINCIPAL,
                tamaño=11,
                peso="bold",
            ).pack(side="right", anchor="e")

            detalle = (
                f"{resultado['operacion']} · "
                f"{resultado['aciertos']} aciertos / {resultado['errores']} errores · "
                f"{resultado['tiempo_segundos']:.1f} s"
            )
            crear_etiqueta(
                fila,
                detalle,
                color=COLOR_TEXTO_SUAVE,
                tamaño=9,
                wraplength=350,
                justify="left",
            ).pack(anchor="w", padx=8, pady=(0, 5))


class JuegoFrame(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, fg_color=COLOR_FONDO)
        self.app = app
        self.estado = "pregunta"
        self.numero_pregunta = 0
        self.puntaje = 0
        self.errores = 0
        self.ejercicio = None
        self.respuesta_correcta = 0
        self.inicio_competencia = None
        self.tiempo_competencia = None
        self.intento_competencia_id = None
        self.temporizador_after = None

        self.titulo = crear_etiqueta(
            self, color=COLOR_PRINCIPAL, tamaño=25, peso="bold"
        )
        self.titulo.pack(pady=(16, 2))

        self.etiqueta_modo = crear_etiqueta(self, color=COLOR_TEXTO_SUAVE)
        self.etiqueta_modo.pack(pady=(0, 4))

        self.panel_estado = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_estado.pack(fill="x", padx=18, pady=3)
        self.progreso = crear_etiqueta(
            self.panel_estado, tamaño=14, peso="bold"
        )
        self.temporizador = TemporizadorCircular(
            self.panel_estado,
            duracion=DURACION_COMPETENCIA_SEGUNDOS,
            tamaño=96,
        )

        self.problema = crear_etiqueta(
            self, color=COLOR_PRINCIPAL, tamaño=38, peso="bold"
        )
        self.problema.pack(pady=(12, 10))

        self.instruccion = crear_etiqueta(
            self, "Escribe el resultado de la operación."
        )
        self.instruccion.pack(pady=(0, 4))

        self.entry_respuesta = crear_entrada(
            self,
            "Tu respuesta",
            width=220,
            height=44,
            justify="center",
        )
        self.entry_respuesta.pack(pady=5)
        self.entry_respuesta.bind(
            "<Return>", lambda _evento: self.accion_principal()
        )

        self.mensaje = crear_etiqueta(self, tamaño=14)
        self.mensaje.pack(pady=(5, 8))

        self.boton_principal = crear_boton(
            self,
            "Comprobar",
            self.accion_principal,
            width=220,
            height=42,
        )
        self.boton_principal.pack(pady=5)

        crear_boton(
            self,
            "Volver al menú",
            self.volver_menu,
            estilo="secundario",
            width=220,
            height=38,
        ).pack(pady=6)

    def al_mostrar(self):
        self._detener_temporizador()
        configuracion = self.app.configuracion_partida
        if not configuracion or not self.app.usuario_actual:
            self.app.mostrar("MenuFrame")
            return

        self.operacion = configuracion["operacion"]
        self.modo = configuracion["modo"]
        self.titulo.configure(text=self.operacion)
        self.etiqueta_modo.configure(text=f"Modo: {self.modo}")
        self.iniciar_partida()

    def volver_menu(self):
        self._detener_temporizador()
        self.app.mostrar("MenuFrame")

    def _configurar_panel_estado(self):
        self.progreso.pack_forget()
        self.temporizador.pack_forget()
        if self.modo == "Competencia":
            self.progreso.pack(side="left", padx=(8, 0), pady=15)
            self.temporizador.pack(side="right", padx=(0, 8), pady=2)
        else:
            self.progreso.pack(pady=5)

    def iniciar_partida(self):
        self._detener_temporizador()
        self.numero_pregunta = 0
        self.puntaje = 0
        self.errores = 0
        self.estado = "pregunta"
        self.inicio_competencia = None
        self.tiempo_competencia = None
        self.intento_competencia_id = None
        self.mensaje.configure(text="", text_color=COLOR_TEXTO_SUAVE)
        self.instruccion.configure(text=obtener_instruccion(self.operacion))
        self.entry_respuesta.configure(state="normal")
        self.boton_principal.configure(
            text="Comprobar",
            state="normal",
            command=self.accion_principal,
        )
        self._configurar_panel_estado()

        if self.modo == "Competencia":
            try:
                self.intento_competencia_id = anuarcoto_db.iniciar_intento_competencia(
                    self.app.usuario_actual["id"], self.operacion
                )
            except sqlite3.Error:
                self.estado = "finalizada"
                self.progreso.configure(text="No se pudo iniciar la competencia")
                self.problema.configure(text="Intenta nuevamente")
                self.instruccion.configure(
                    text="No fue posible registrar tu intento en la base de datos."
                )
                self.entry_respuesta.configure(state="disabled")
                self.boton_principal.configure(
                    text="Volver al menú",
                    command=self.volver_menu,
                )
                self.mensaje.configure(
                    text="No se inició la partida.", text_color=COLOR_ERROR
                )
                return

        self.mostrar_siguiente_pregunta()
        if self.modo == "Competencia":
            self.temporizador.actualizar(DURACION_COMPETENCIA_SEGUNDOS)
            self.inicio_competencia = time.perf_counter()
            self._actualizar_temporizador()

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
        self.entry_respuesta.focus_set()

    def _actualizar_progreso(self):
        if self.modo == "Competencia":
            texto = (
                f"Pregunta {self.numero_pregunta} de {NUM_PREGUNTAS}"
                f"  |  ✓ {self.puntaje}  ✗ {self.errores}"
            )
        else:
            texto = (
                f"Pregunta {self.numero_pregunta} de {NUM_PREGUNTAS}"
                f"    |    Puntos: {self.puntaje}"
            )
        self.progreso.configure(text=texto)

    def accion_principal(self):
        if self.estado == "pregunta":
            self.comprobar_respuesta()
        elif self.estado == "respondida":
            if self.numero_pregunta < NUM_PREGUNTAS:
                self.mostrar_siguiente_pregunta()
            else:
                self.finalizar_partida()
        elif self.estado == "finalizada":
            if self.modo == "Competencia" and not anuarcoto_db.puede_iniciar_competencia(
                self.app.usuario_actual["id"]
            ):
                self.mensaje.configure(
                    text="Ya utilizaste tus 3 intentos de Competencia de hoy.",
                    text_color=COLOR_ERROR,
                )
                self.boton_principal.configure(state="disabled")
                return
            self.iniciar_partida()

    def comprobar_respuesta(self):
        if self.modo == "Competencia" and self._tiempo_transcurrido() >= DURACION_COMPETENCIA_SEGUNDOS:
            self.finalizar_partida(tiempo_agotado=True)
            return

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
            self.errores += 1
            self.mensaje.configure(
                text=f"No es correcto. La respuesta era {self.respuesta_correcta}.",
                text_color=COLOR_ERROR,
            )

        self._actualizar_progreso()
        if self.modo == "Competencia" and self.numero_pregunta == NUM_PREGUNTAS:
            self.finalizar_partida()
            return

        siguiente_texto = (
            "Siguiente pregunta"
            if self.numero_pregunta < NUM_PREGUNTAS
            else "Ver resultado"
        )
        self.boton_principal.configure(text=siguiente_texto)

    def _tiempo_transcurrido(self):
        if self.inicio_competencia is None:
            return 0.0
        return time.perf_counter() - self.inicio_competencia

    def _actualizar_temporizador(self):
        self.temporizador_after = None
        if self.estado == "finalizada" or self.inicio_competencia is None:
            return

        transcurrido = self._tiempo_transcurrido()
        restante = max(0.0, DURACION_COMPETENCIA_SEGUNDOS - transcurrido)
        self.temporizador.actualizar(restante)
        if restante <= 0:
            self.finalizar_partida(tiempo_agotado=True)
            return

        self.temporizador_after = self.after(100, self._actualizar_temporizador)

    def _detener_temporizador(self):
        if self.temporizador_after is not None:
            try:
                self.after_cancel(self.temporizador_after)
            except (tk.TclError, ValueError, RuntimeError):
                pass
            self.temporizador_after = None

    def finalizar_partida(self, tiempo_agotado=False):
        if self.estado == "finalizada":
            return

        if self.modo == "Competencia":
            self.tiempo_competencia = min(
                DURACION_COMPETENCIA_SEGUNDOS,
                self._tiempo_transcurrido(),
            )
        self.estado = "finalizada"
        self._detener_temporizador()
        self.progreso.configure(
            text="Competencia terminada" if self.modo == "Competencia" else "Partida terminada"
        )
        self.problema.configure(text=f"{self.puntaje} / {NUM_PREGUNTAS}")
        porcentaje = round((self.puntaje / NUM_PREGUNTAS) * 100)
        if self.modo == "Competencia":
            puntaje_neto = self.puntaje - self.errores
            if tiempo_agotado:
                texto = (
                    f"Tiempo agotado. Aciertos: {self.puntaje} · "
                    f"Errores: {self.errores} · Puntaje: {puntaje_neto:+d}."
                )
            else:
                texto = (
                    f"Completaste los ejercicios en {self.tiempo_competencia:.2f} s. "
                    f"Aciertos: {self.puntaje} · Errores: {self.errores} · "
                    f"Puntaje: {puntaje_neto:+d}."
                )
            self.instruccion.configure(text=texto)
            self._guardar_resultado_competencia()
        else:
            self.instruccion.configure(
                text=f"Tu resultado: {porcentaje}% de respuestas correctas."
            )
            self.mensaje.configure(
                text="Resultado de práctica: no se guardó.",
                text_color=COLOR_TEXTO_SUAVE,
            )

        self.entry_respuesta.configure(state="disabled")
        if self.modo == "Competencia" and not anuarcoto_db.puede_iniciar_competencia(
            self.app.usuario_actual["id"]
        ):
            self.boton_principal.configure(
                text="Límite diario alcanzado",
                state="disabled",
            )
        else:
            self.boton_principal.configure(
                text="Jugar otra vez",
                state="normal",
            )

    def _guardar_resultado_competencia(self):
        try:
            if self.intento_competencia_id is None:
                raise sqlite3.DatabaseError("No hay un intento competitivo activo.")
            anuarcoto_db.finalizar_intento_competencia(
                self.intento_competencia_id,
                self.puntaje,
                self.errores,
                self.tiempo_competencia,
            )
            self.intento_competencia_id = None
        except sqlite3.Error:
            texto = "No se pudo guardar el resultado en la base de datos."
            color = COLOR_ERROR
        else:
            texto = "Tu resultado se guardó correctamente."
            color = COLOR_EXITO
        self.mensaje.configure(text=texto, text_color=color)
