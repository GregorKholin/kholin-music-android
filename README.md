# Kholin Music (Android) — Fase 1

App independiente para Android hecha con Kivy. **Fase 1**: reproduce la música
que ya tengas copiada en el teléfono. Todavía no descarga de YouTube (eso es
la fase 2).

## Cómo usarla
1. Instalá el `.apk` en tu teléfono (activá "Instalar apps de orígenes
   desconocidos" la primera vez que lo intentes).
2. Copiále tus archivos `.mp3`/`.ogg`/`.m4a` a la carpeta
   `Music/KholinMusic` del teléfono (por cable USB o donde prefieras).
3. Abrí la app y tocá "Actualizar" si no aparecen solas.

## Cómo se compila
El `.apk` se arma automáticamente en GitHub Actions (ver
`.github/workflows/build.yml`) cada vez que se sube algo a `main`/`master`,
usando Buildozer. No hace falta instalar nada localmente para generarlo.
