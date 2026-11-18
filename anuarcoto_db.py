import hashlib
import hmac
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anuarcoto.db")
ITERACIONES = 100_000
MAX_INTENTOS_COMPETENCIA = 3
# Activar al terminar las pruebas para limitar a 3 competencias por día.
LIMITE_INTENTOS_COMPETENCIA_ACTIVO = False


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
                tiempo_segundos REAL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )
        columnas = {
            fila["name"] for fila in con.execute("PRAGMA table_info(partidas)")
        }
        if "tiempo_segundos" not in columnas:
            con.execute("ALTER TABLE partidas ADD COLUMN tiempo_segundos REAL")


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


def guardar_partida(usuario_id, operacion, modo, puntaje, tiempo_segundos=None):
    with conectar() as con:
        con.execute(
            "INSERT INTO partidas "
            "(usuario_id, operacion, modo, puntaje, fecha, tiempo_segundos) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                usuario_id,
                operacion,
                modo,
                puntaje,
                datetime.now().isoformat(timespec="seconds"),
                tiempo_segundos,
            ),
        )


def iniciar_intento_competencia(usuario_id, operacion):
    with conectar() as con:
        cursor = con.execute(
            "INSERT INTO partidas "
            "(usuario_id, operacion, modo, puntaje, fecha, tiempo_segundos) "
            "VALUES (?, ?, 'Competencia', 0, ?, NULL)",
            (
                usuario_id,
                operacion,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        return cursor.lastrowid


def finalizar_intento_competencia(partida_id, puntaje, tiempo_segundos):
    with conectar() as con:
        cursor = con.execute(
            "UPDATE partidas SET puntaje = ?, tiempo_segundos = ? "
            "WHERE id = ? AND modo = 'Competencia' AND tiempo_segundos IS NULL",
            (puntaje, tiempo_segundos, partida_id),
        )
        if cursor.rowcount != 1:
            raise sqlite3.DatabaseError("No se encontró el intento competitivo activo.")


def partidas_competencia_hoy(usuario_id):
    hoy = datetime.now().strftime("%Y-%m-%d")
    with conectar() as con:
        fila = con.execute(
            "SELECT COUNT(*) AS total FROM partidas "
            "WHERE usuario_id = ? AND modo = 'Competencia' AND fecha LIKE ?",
            (usuario_id, hoy + "%"),
        ).fetchone()
    return fila["total"]


def puede_iniciar_competencia(usuario_id):
    if not LIMITE_INTENTOS_COMPETENCIA_ACTIVO:
        return True
    return partidas_competencia_hoy(usuario_id) < MAX_INTENTOS_COMPETENCIA


def obtener_ranking_competencia(operacion, limite=10):
    with conectar() as con:
        filas = con.execute(
            "SELECT u.id AS usuario_id, u.nombre, p.puntaje, "
            "p.tiempo_segundos, p.fecha "
            "FROM partidas p JOIN usuarios u ON u.id = p.usuario_id "
            "WHERE p.modo = 'Competencia' AND p.operacion = ? "
            "AND p.tiempo_segundos IS NOT NULL",
            (operacion,),
        ).fetchall()

    resultados_por_usuario = {}
    for fila in filas:
        resultados_por_usuario.setdefault(fila["usuario_id"], {
            "usuario_id": fila["usuario_id"],
            "nombre": fila["nombre"],
            "intentos": [],
        })["intentos"].append(fila)

    ranking = []
    for usuario in resultados_por_usuario.values():
        mejores = sorted(
            usuario["intentos"],
            key=lambda intento: (
                -intento["puntaje"],
                intento["tiempo_segundos"],
                intento["fecha"],
            ),
        )[:MAX_INTENTOS_COMPETENCIA]
        cantidad = len(mejores)
        promedio_aciertos = sum(item["puntaje"] for item in mejores) / cantidad
        promedio_tiempo = sum(item["tiempo_segundos"] for item in mejores) / cantidad
        ranking.append(
            {
                "usuario_id": usuario["usuario_id"],
                "nombre": usuario["nombre"],
                "promedio_aciertos": round(promedio_aciertos, 2),
                "promedio_tiempo": round(promedio_tiempo, 2),
                "intentos_considerados": cantidad,
            }
        )

    ranking.sort(
        key=lambda item: (
            -item["promedio_aciertos"],
            item["promedio_tiempo"],
            item["nombre"].casefold(),
        )
    )
    return ranking[:max(0, limite)]
