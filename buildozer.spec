[app]
title = Kholin Music
package.name = kholinmusic
package.domain = org.gregor

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy==2.3.1,mutagen,pyjnius

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.png

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

android.api = 34
android.minapi = 24
android.ndk_api = 24
android.ndk = 25b
android.archs = arm64-v8a

# Buildozer clona python-for-android desde git (no usa el paquete pip
# instalado) en .buildozer/android/platform/python-for-android. Sin fijar
# esto, agarra la rama "master" (HEAD mas nuevo, hoy equivalente a
# v2026.05.09), que es la version que en realidad rompia el build con el
# --python-version 3.14.2 mal calculado. Fijamos el tag estable que ya
# habiamos probado por pip.
p4a.branch = v2023.09.16

[buildozer]
log_level = 2
warn_on_root = 1
