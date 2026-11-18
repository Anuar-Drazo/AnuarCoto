import math
import tkinter as tk

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLOR_FONDO = "#f4f1fa"
COLOR_PRINCIPAL = "#6c4ab6"
COLOR_HOVER = "#573a96"
COLOR_TEXTO_SUAVE = "#6b6475"
COLOR_ERROR = "#c0392b"
COLOR_EXITO = "#218c54"
COLOR_TIMER_AZUL = "#243B73"
COLOR_TIMER_AMARILLO = "#E0B323"
COLOR_TIMER_ROJO = "#C0392B"
NUM_PREGUNTAS = 10
FUENTE = "Century Gothic"

ESTILOS_BOTON = {
    "principal": {
        "fg_color": COLOR_PRINCIPAL,
        "hover_color": COLOR_HOVER,
    },
    "secundario": {
        "fg_color": "transparent",
        "border_width": 2,
        "text_color": COLOR_PRINCIPAL,
        "border_color": COLOR_PRINCIPAL,
        "hover_color": "#e6def5",
    },
    "deshabilitado": {
        "fg_color": "#c9c2d4",
        "hover_color": "#c9c2d4",
        "text_color": "#f7f6f9",
    },
}


def fuente(tamaño=14, peso="normal"):
    return ctk.CTkFont(family=FUENTE, size=tamaño, weight=peso)


def crear_etiqueta(parent, texto="", *, color=None, tamaño=14, peso="normal", **opciones):
    if color is not None:
        opciones["text_color"] = color
    opciones["font"] = fuente(tamaño, peso)
    return ctk.CTkLabel(parent, text=texto, **opciones)


def crear_entrada(parent, placeholder, *, password=False, width=260, height=40, **opciones):
    if password:
        opciones["show"] = "*"
    opciones["font"] = fuente()
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        width=width,
        height=height,
        **opciones,
    )


def crear_boton(
    parent,
    texto,
    comando,
    *,
    estilo="principal",
    width=260,
    height=42,
    state="normal",
    **opciones,
):
    configuracion = ESTILOS_BOTON[estilo].copy()
    configuracion.update(opciones)
    configuracion["font"] = fuente()
    return ctk.CTkButton(
        parent,
        text=texto,
        command=comando,
        width=width,
        height=height,
        state=state,
        **configuracion,
    )


def limpiar_entradas(*entradas):
    for entrada in entradas:
        entrada.delete(0, "end")
        entrada._activate_placeholder()


class TemporizadorCircular(ctk.CTkFrame):
    def __init__(self, parent, duracion, tamaño=104):
        super().__init__(
            parent,
            fg_color="transparent",
            width=tamaño,
            height=tamaño,
        )
        self.duracion = duracion
        self.restante = float(duracion)
        self.canvas = tk.Canvas(
            self,
            width=tamaño,
            height=tamaño,
            bg=COLOR_FONDO,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self._dibujar)
        self._dibujar()

    def actualizar(self, restante):
        self.restante = max(0.0, min(float(self.duracion), float(restante)))
        self._dibujar()

    def _dibujar(self, _evento=None):
        ancho = max(1, self.canvas.winfo_width())
        alto = max(1, self.canvas.winfo_height())
        lado = min(ancho, alto)
        margen = max(8, int(lado * 0.12))
        centro_x = ancho / 2
        centro_y = alto / 2
        caja = (
            centro_x - lado / 2 + margen,
            centro_y - lado / 2 + margen,
            centro_x + lado / 2 - margen,
            centro_y + lado / 2 - margen,
        )
        grosor = max(5, int(lado * 0.085))
        proporcion = self.restante / self.duracion

        if self.restante > 30:
            color = COLOR_TIMER_AZUL
        elif self.restante > 10:
            color = COLOR_TIMER_AMARILLO
        else:
            color = COLOR_TIMER_ROJO

        self.canvas.delete("all")
        self.canvas.create_oval(
            *caja,
            outline="#ded8e8",
            width=grosor,
        )
        if proporcion > 0:
            self.canvas.create_arc(
                *caja,
                start=90,
                extent=-359.9 * proporcion,
                style="arc",
                outline=color,
                width=grosor,
            )

        tamaño_texto = max(12, int(lado * 0.19))
        self.canvas.create_text(
            centro_x,
            centro_y - 3,
            text=str(math.ceil(self.restante)),
            fill=COLOR_PRINCIPAL,
            font=(FUENTE, tamaño_texto, "bold"),
        )
        self.canvas.create_text(
            centro_x,
            centro_y + tamaño_texto * 0.9,
            text="seg",
            fill=COLOR_TEXTO_SUAVE,
            font=(FUENTE, max(8, int(lado * 0.085))),
        )
