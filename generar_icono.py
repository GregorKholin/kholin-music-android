from PIL import Image, ImageDraw

TAMANO = 512
COLOR_FONDO = (18, 60, 122)

img = Image.new("RGBA", (TAMANO, TAMANO), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
margen = TAMANO // 16
radio = TAMANO // 5
draw.rounded_rectangle([margen, margen, TAMANO - margen, TAMANO - margen], radius=radio, fill=COLOR_FONDO)

cx, cy = TAMANO * 0.42, TAMANO * 0.66
r = TAMANO * 0.13
draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="white")

palito_x = cx + r * 0.85
draw.rectangle([palito_x, TAMANO * 0.18, palito_x + max(1, TAMANO * 0.06), cy], fill="white")

draw.polygon(
    [
        (palito_x, TAMANO * 0.18),
        (palito_x + TAMANO * 0.28, TAMANO * 0.26),
        (palito_x + TAMANO * 0.28, TAMANO * 0.40),
        (palito_x, TAMANO * 0.34),
    ],
    fill="white",
)

img.save("icon.png")
print("listo")
