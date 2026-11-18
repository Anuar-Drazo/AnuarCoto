import hashlib
import hmac
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anuarcoto.db")
ITERACIONES = 100_000
MAX_INTENTOS_COMPETENCIA = 3
LIMITE_INTENTOS_COMPETENCIA_ACTIVO = True


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
                aciertos INTEGER,
                errores INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )
        columnas = {
            fila["name"] for fila in con.execute("PRAGMA table_info(partidas)")
        }
        if "tiempo_segundos" not in columnas:
            con.execute("ALTER TABLE partidas ADD COLUMN tiempo_segundos REAL")
        if "aciertos" not in columnas:
            con.execute("ALTER TABLE partidas ADD COLUMN aciertos INTEGER")
        if "errores" not in columnas:
            con.execute("ALTER TABLE partidas ADD COLUMN errores INTEGER")


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
            "(usuario_id, operacion, modo, puntaje, fecha, tiempo_segundos, aciertos, errores) "
            "VALUES (?, ?, 'Competencia', 0, ?, NULL, NULL, NULL)",
            (
                usuario_id,
                operacion,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        return cursor.lastrowid


def finalizar_intento_competencia(partida_id, aciertos, errores, tiempo_segundos):
    puntaje = aciertos - errores
    with conectar() as con:
        cursor = con.execute(
            "UPDATE partidas SET puntaje = ?, aciertos = ?, errores = ?, tiempo_segundos = ? "
            "WHERE id = ? AND modo = 'Competencia' AND tiempo_segundos IS NULL",
            (puntaje, aciertos, errores, tiempo_segundos, partida_id),
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


def obtener_ranking_competencia(operacion=None, criterio="ritmo", limite=10):
    if criterio not in {"ritmo", "puntaje"}:
        raise ValueError("El criterio debe ser 'ritmo' o 'puntaje'.")

    filtro_operacion = ""
    parametros = []
    if operacion is not None:
        filtro_operacion = "AND p.operacion = ? "
        parametros.append(operacion)

    with conectar() as con:
        filas = con.execute(
            "SELECT u.id AS usuario_id, u.nombre, p.operacion, p.puntaje, "
            "p.aciertos, p.errores, p.tiempo_segundos, p.fecha "
            "FROM partidas p JOIN usuarios u ON u.id = p.usuario_id "
            "WHERE p.modo = 'Competencia' AND p.tiempo_segundos IS NOT NULL "
            "AND p.aciertos IS NOT NULL AND p.errores IS NOT NULL "
            + filtro_operacion,
            parametros,
        ).fetchall()

    mejores_por_usuario = {}
    for fila in filas:
        tiempo = max(float(fila["tiempo_segundos"]), 0.01)
        intento = dict(fila)
        intento["aciertos_por_segundo"] = intento["aciertos"] / tiempo

        if criterio == "ritmo":
            clave = (
                -intento["aciertos_por_segundo"],
                -intento["puntaje"],
                tiempo,
                intento["fecha"],
            )
        else:
            clave = (
                -intento["puntaje"],
                -intento["aciertos_por_segundo"],
                tiempo,
                intento["fecha"],
            )

        usuario_id = intento["usuario_id"]
        actual = mejores_por_usuario.get(usuario_id)
        if actual is None or clave < actual[0]:
            mejores_por_usuario[usuario_id] = (clave, intento)

    ranking = [item[1] for item in mejores_por_usuario.values()]
    ranking.sort(
        key=lambda item: (
            -item["aciertos_por_segundo"] if criterio == "ritmo" else -item["puntaje"],
            -item["puntaje"] if criterio == "ritmo" else -item["aciertos_por_segundo"],
            item["tiempo_segundos"],
            item["nombre"].casefold(),
        )
    )
    return ranking[:max(0, limite)]
