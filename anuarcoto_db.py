import hashlib
import hmac
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anuarcoto.db")
ITERACIONES = 100_000


def conectar():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar():
    with conectar() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                fecha_registro TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                operacion TEXT NOT NULL,
                modo TEXT NOT NULL,
                puntaje INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )



def crear_hash(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERACIONES)
    return hash_bytes.hex(), salt.hex()


def verificar(password, hash_guardado, salt_guardado):
    nuevo_hash, _ = crear_hash(password, bytes.fromhex(salt_guardado))
    return hmac.compare_digest(nuevo_hash, hash_guardado)



def registrar_usuario(nombre, password):
    nombre = nombre.strip()
    if len(nombre) < 3 or len(nombre) > 20:
        return False, "El usuario debe tener entre 3 y 20 caracteres."
    if len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres."

    hash_hex, salt_hex = crear_hash(password)
    try:
        with conectar() as con:
            con.execute(
                "INSERT INTO usuarios (nombre, password_hash, salt, fecha_registro) "
                "VALUES (?, ?, ?, ?)",
                (nombre, hash_hex, salt_hex, datetime.now().isoformat(timespec="seconds")),
            )
    except sqlite3.IntegrityError:
        return False, "Ese nombre de usuario ya existe."
    return True, "Cuenta creada correctamente."


def validar_login(nombre, password):
    with conectar() as con:
        fila = con.execute(
            "SELECT id, nombre, password_hash, salt FROM usuarios WHERE nombre = ?",
            (nombre.strip(),),
        ).fetchone()
    if fila and verificar(password, fila["password_hash"], fila["salt"]):
        return {"id": fila["id"], "nombre": fila["nombre"]}
    return None



def guardar_partida(usuario_id, operacion, modo, puntaje):
    with conectar() as con:
        con.execute(
            "INSERT INTO partidas (usuario_id, operacion, modo, puntaje, fecha) "
            "VALUES (?, ?, ?, ?, ?)",
            (usuario_id, operacion, modo, puntaje, datetime.now().isoformat(timespec="seconds")),
        )


def partidas_competencia_hoy(usuario_id):
    hoy = datetime.now().strftime("%Y-%m-%d")
    with conectar() as con:
        fila = con.execute(
            "SELECT COUNT(*) AS total FROM partidas "
            "WHERE usuario_id = ? AND modo = 'Competencia' AND fecha LIKE ?",
            (usuario_id, hoy + "%"),
        ).fetchone()
    return fila["total"]