"""Escanea una carpeta del teléfono y vuelca metadata a la base local."""
import os

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis

import db

EXTENSIONES_VALIDAS = (".mp3", ".m4a", ".ogg", ".wav")


def _nombre_desde_archivo(ruta):
    return os.path.splitext(os.path.basename(ruta))[0]


def _leer_metadata(ruta):
    extension = os.path.splitext(ruta)[1].lower()
    titulo = _nombre_desde_archivo(ruta)
    artista = "Desconocido"
    album = "Desconocido"
    duracion = None

    try:
        if extension == ".mp3":
            audio = EasyID3(ruta)
            titulo = audio.get("title", [titulo])[0]
            artista = audio.get("artist", [artista])[0]
            album = audio.get("album", [album])[0]
        elif extension == ".m4a":
            audio = MP4(ruta)
            if audio.tags:
                titulo = (audio.tags.get("\xa9nam", [titulo]) or [titulo])[0]
                artista = (audio.tags.get("\xa9ART", [artista]) or [artista])[0]
                album = (audio.tags.get("\xa9alb", [album]) or [album])[0]
        elif extension == ".ogg":
            audio = OggVorbis(ruta)
            titulo = (audio.get("title", [titulo]) or [titulo])[0]
            artista = (audio.get("artist", [artista]) or [artista])[0]
            album = (audio.get("album", [album]) or [album])[0]
    except Exception:
        pass

    try:
        info = MutagenFile(ruta)
        if info is not None and info.info is not None:
            duracion = info.info.length
    except Exception:
        pass

    return titulo, artista, album, duracion


def escanear_carpeta(ruta_db, carpeta):
    if not os.path.isdir(carpeta):
        return 0

    filepaths_encontrados = []
    contador = 0

    for raiz, _dirs, archivos in os.walk(carpeta):
        for nombre_archivo in archivos:
            if not nombre_archivo.lower().endswith(EXTENSIONES_VALIDAS):
                continue
            ruta_completa = os.path.join(raiz, nombre_archivo)
            filepaths_encontrados.append(ruta_completa)
            titulo, artista, album, duracion = _leer_metadata(ruta_completa)
            db.guardar_o_actualizar_cancion(ruta_db, ruta_completa, titulo, artista, album, duracion)
            contador += 1

    db.eliminar_canciones_faltantes(ruta_db, filepaths_encontrados)
    return contador
