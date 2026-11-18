from dataclasses import dataclass
import random


OPERACIONES = [
    "Suma de 2 dígitos",
    "Resta de 2 dígitos",
    "Multiplicación (2 dígitos × 1)",
    "División exacta",
]


@dataclass(frozen=True)
class Ejercicio:

    numero_a: int
    numero_b: int
    simbolo: str
    respuesta_correcta: int

    @property
    def expresion(self):
        return f"{self.numero_a} {self.simbolo} {self.numero_b} = ?"


def _generar_suma():
    numero_a = random.randint(10, 99)
    numero_b = random.randint(10, 99)
    return Ejercicio(numero_a, numero_b, "+", numero_a + numero_b)


def _generar_resta():
    numero_a = random.randint(10, 99)
    numero_b = random.randint(10, numero_a)
    return Ejercicio(numero_a, numero_b, "−", numero_a - numero_b)


def _generar_multiplicacion():
    numero_a = random.randint(10, 99)
    numero_b = random.randint(2, 9)
    return Ejercicio(numero_a, numero_b, "×", numero_a * numero_b)


def _generar_division():
    divisor = random.randint(2, 9)
    cociente_minimo = (10 + divisor - 1) // divisor
    cociente_maximo = 99 // divisor
    cociente = random.randint(cociente_minimo, cociente_maximo)
    dividendo = divisor * cociente
    return Ejercicio(dividendo, divisor, "÷", cociente)


_GENERADORES = {
    OPERACIONES[0]: _generar_suma,
    OPERACIONES[1]: _generar_resta,
    OPERACIONES[2]: _generar_multiplicacion,
    OPERACIONES[3]: _generar_division,
}

_INSTRUCCIONES = {
    OPERACIONES[0]: "Escribe el resultado de la suma.",
    OPERACIONES[1]: "Escribe el resultado de la resta.",
    OPERACIONES[2]: "Escribe el resultado de la multiplicación.",
    OPERACIONES[3]: "Escribe el resultado de la división.",
}


def generar_ejercicio(operacion):
    """Genera un ejercicio válido para la operación seleccionada.

    Raises:
        ValueError: si la operación no está entre las cuatro disponibles.
    """
    generador = _GENERADORES.get(operacion)
    if generador is None:
        raise ValueError(f"Operación no reconocida: {operacion}")
    return generador()


def obtener_instruccion(operacion):
    """Devuelve la instrucción que debe mostrarse para una operación."""
    try:
        return _INSTRUCCIONES[operacion]
    except KeyError:
        raise ValueError(f"Operación no reconocida: {operacion}") from None


def comprobar_respuesta(respuesta_usuario, ejercicio):
    """Indica si la respuesta entera del usuario es correcta."""
    return respuesta_usuario == ejercicio.respuesta_correcta
