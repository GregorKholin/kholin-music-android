"""Base de datos local de la app (SQLite) — versión mínima para el teléfono:
solo canciones, sin playlists todavía (eso viene en una fase siguiente)."""
import sqlite3


def obtener_conexion(ruta_db):
    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db(ruta_db):
    conexion = obtener_conexion(ruta_db)
    conexion.executescript(
        """
        CREATE TABLE IF NOT EXISTS canciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE NOT NULL,
            titulo TEXT NOT NULL,
            artista TEXT NOT NULL DEFAULT 'Desconocido',
            album TEXT NOT NULL DEFAULT 'Desconocido',
            duracion REAL
        );
        """
    )
    conexion.commit()
    conexion.close()


def guardar_o_actualizar_cancion(ruta_db, filepath, titulo, artista, album, duracion):
    conexion = obtener_conexion(ruta_db)
    fila = conexion.execute("SELECT id FROM canciones WHERE filepath = ?", (filepath,)).fetchone()
    if fila:
        conexion.execute(
            "UPDATE canciones SET titulo=?, artista=?, album=?, duracion=? WHERE id=?",
            (titulo, artista, album, duracion, fila["id"]),
        )
    else:
        conexion.execute(
            "INSERT INTO canciones (filepath, titulo, artista, album, duracion) VALUES (?, ?, ?, ?, ?)",
            (filepath, titulo, artista, album, duracion),
        )
    conexion.commit()
    conexion.close()


def obtener_canciones(ruta_db):
    conexion = obtener_conexion(ruta_db)
    filas = conexion.execute("SELECT * FROM canciones ORDER BY titulo COLLATE NOCASE").fetchall()
    conexion.close()
    return [dict(f) for f in filas]


def eliminar_canciones_faltantes(ruta_db, filepaths_existentes):
    conexion = obtener_conexion(ruta_db)
    filas = conexion.execute("SELECT id, filepath FROM canciones").fetchall()
    for fila in filas:
        if fila["filepath"] not in filepaths_existentes:
            conexion.execute("DELETE FROM canciones WHERE id = ?", (fila["id"],))
    conexion.commit()
    conexion.close()
