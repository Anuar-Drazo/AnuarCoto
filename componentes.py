import customtkinter as ctk

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


def fuente(tamano=14, peso="normal"):
    return ctk.CTkFont(family=FUENTE, size=tamano, weight=peso)


def crear_etiqueta(parent, texto="", *, color=None, tamano=14, peso="normal", **opciones):
    if color is not None:
        opciones["text_color"] = color
    opciones["font"] = fuente(tamano, peso)
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
