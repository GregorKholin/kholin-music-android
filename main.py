"""Kholin Music (Android) — Fase 1: reproduce la música que ya tenés copiada
en el teléfono (carpeta Music/KholinMusic). Sin descarga de YouTube todavía."""
import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

import db
import scanner

if platform == "android":
    from android.permissions import Permission, request_permissions
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    CARPETA_MUSICA = "/storage/emulated/0/Music/KholinMusic"
else:
    CARPETA_MUSICA = os.path.join(os.path.expanduser("~"), "KholinMusicTest")

KV = """
<FilaCancion>:
    size_hint_y: None
    height: dp(64)
    padding: dp(8)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: (0.29, 0.29, 0.33, 1) if not root.activa else (0.42, 0.38, 0.75, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]

    BoxLayout:
        size_hint_x: None
        width: dp(48)
        canvas.before:
            Color:
                rgba: (0.55, 0.5, 0.9, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(8)]

    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.titulo
            bold: True
            halign: "left"
            valign: "middle"
            text_size: self.size
            shorten: True
        Label:
            text: root.subtitulo
            color: (0.7, 0.7, 0.75, 1)
            halign: "left"
            valign: "middle"
            text_size: self.size
            font_size: "12sp"
            shorten: True

    Label:
        text: root.duracion_texto
        size_hint_x: None
        width: dp(50)
        color: (0.7, 0.7, 0.75, 1)

RootWidget:
    orientation: "vertical"
    canvas.before:
        Color:
            rgba: (0.05, 0.05, 0.06, 1)
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: None
        height: dp(70)
        padding: dp(12)
        canvas.before:
            Color:
                rgba: (0.07, 0.15, 0.35, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "KHOLIN MUSIC"
            bold: True
            font_size: "20sp"
        Button:
            text: "Actualizar"
            size_hint_x: None
            width: dp(110)
            on_release: app.actualizar_biblioteca()

    ScrollView:
        do_scroll_x: False
        BoxLayout:
            id: lista_canciones
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(4)
            padding: dp(8)

    BoxLayout:
        id: miniplayer
        size_hint_y: None
        height: dp(90)
        padding: dp(10)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: (0.04, 0.05, 0.09, 1)
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_x: None
            width: dp(60)
            canvas.before:
                Color:
                    rgba: (0.55, 0.5, 0.9, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(8)]

        BoxLayout:
            orientation: "vertical"
            size_hint_x: 0.4
            Label:
                id: label_titulo_mini
                text: "Nada sonando"
                bold: True
                halign: "left"
                text_size: self.size
                shorten: True
            Label:
                id: label_artista_mini
                text: ""
                color: (0.7, 0.7, 0.75, 1)
                halign: "left"
                text_size: self.size
                font_size: "12sp"
                shorten: True

        Button:
            text: "<"
            size_hint_x: None
            width: dp(44)
            on_release: app.anterior()
        Button:
            id: boton_play
            text: ">"
            size_hint_x: None
            width: dp(44)
            on_release: app.play_pausa()
        Button:
            text: ">|"
            size_hint_x: None
            width: dp(44)
            on_release: app.siguiente()
"""


def formatear_duracion(segundos):
    if not segundos:
        return "0:00"
    segundos = int(segundos)
    minutos, segs = divmod(segundos, 60)
    return f"{minutos}:{segs:02d}"


class FilaCancion(BoxLayout):
    titulo = StringProperty("")
    subtitulo = StringProperty("")
    duracion_texto = StringProperty("")
    indice = NumericProperty(0)
    activa = BooleanProperty(False)


class RootWidget(BoxLayout):
    pass


class KholinMusicApp(App):
    canciones = ListProperty([])
    indice_actual = NumericProperty(-1)
    en_pausa = BooleanProperty(False)

    def build(self):
        Builder.load_string(KV)
        self.sonido = None
        self.filas_widgets = []
        root = RootWidget()
        self.root_widget = root
        Clock.schedule_once(lambda dt: self.cargar_biblioteca(), 0.3)
        Clock.schedule_interval(self._chequear_fin_cancion, 0.5)
        return root

    def _ruta_db(self):
        return os.path.join(self.user_data_dir, "biblioteca.db")

    def cargar_biblioteca(self):
        db.inicializar_db(self._ruta_db())
        self._refrescar_lista()
        if not self.canciones:
            self.actualizar_biblioteca()

    def actualizar_biblioteca(self):
        threading.Thread(target=self._tarea_escanear, daemon=True).start()

    def _tarea_escanear(self):
        os.makedirs(CARPETA_MUSICA, exist_ok=True)
        scanner.escanear_carpeta(self._ruta_db(), CARPETA_MUSICA)
        Clock.schedule_once(lambda dt: self._refrescar_lista(), 0)

    def _refrescar_lista(self):
        self.canciones = db.obtener_canciones(self._ruta_db())
        contenedor = self.root_widget.ids.lista_canciones
        contenedor.clear_widgets()
        self.filas_widgets = []

        if not self.canciones:
            contenedor.add_widget(Label(
                text=f"No hay canciones en:\n{CARPETA_MUSICA}\n\nCopiá tus mp3/ogg ahí y tocá 'Actualizar'.",
                size_hint_y=None, height=120,
            ))
            return

        for i, cancion in enumerate(self.canciones):
            fila = FilaCancion(
                titulo=cancion["titulo"],
                subtitulo=cancion["artista"],
                duracion_texto=formatear_duracion(cancion.get("duracion")),
                indice=i,
                activa=(i == self.indice_actual),
            )
            fila.bind(on_touch_down=self._al_tocar_fila)
            contenedor.add_widget(fila)
            self.filas_widgets.append(fila)

    def _al_tocar_fila(self, widget, touch):
        if widget.collide_point(*touch.pos):
            self.reproducir_indice(widget.indice)
            return True
        return False

    def reproducir_indice(self, indice):
        if not (0 <= indice < len(self.canciones)):
            return
        if self.sonido:
            self.sonido.stop()
            self.sonido.unload()

        cancion = self.canciones[indice]
        self.sonido = SoundLoader.load(cancion["filepath"])
        if self.sonido:
            self.sonido.play()
        self.en_pausa = False
        self.indice_actual = indice

        ids = self.root_widget.ids
        ids.label_titulo_mini.text = cancion["titulo"]
        ids.label_artista_mini.text = cancion["artista"]
        ids.boton_play.text = "||"

        for i, fila in enumerate(self.filas_widgets):
            fila.activa = (i == indice)

    def play_pausa(self):
        if not self.sonido:
            if self.canciones:
                self.reproducir_indice(0)
            return
        if self.en_pausa:
            self.sonido.play()
            self.en_pausa = False
            self.root_widget.ids.boton_play.text = "||"
        else:
            self.sonido.stop()
            self.en_pausa = True
            self.root_widget.ids.boton_play.text = ">"

    def siguiente(self):
        if not self.canciones:
            return
        self.reproducir_indice((self.indice_actual + 1) % len(self.canciones))

    def anterior(self):
        if not self.canciones:
            return
        self.reproducir_indice((self.indice_actual - 1) % len(self.canciones))

    def _chequear_fin_cancion(self, dt):
        if self.sonido and not self.en_pausa and self.sonido.state == "stop" and self.indice_actual != -1:
            self.siguiente()


if __name__ == "__main__":
    KholinMusicApp().run()
