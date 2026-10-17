"""Generate 100% synthetic Spanish/Chile fixtures. Seeded, reproducible."""
import csv
import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seidor_cl import rut_check_digit  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "fixtures"
rng = random.Random(21719)

NOMBRES = ["Camila", "Matías", "Valentina", "Joaquín", "Fernanda", "Sebastián", "Daniela", "Tomás"]
APELLIDOS = ["Rojas", "Muñoz", "Soto", "Contreras", "Silva", "Fuentes", "Araya", "Tapia"]


def name():
    return f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"


def valid_rut(fmt="dots"):
    body = rng.randint(6_000_000, 25_000_000)
    dv = rut_check_digit(body)
    if fmt == "dots":
        return f"{body:,}".replace(",", ".") + f"-{dv}"
    if fmt == "dash":
        return f"{body}-{dv}"
    return f"{body}{dv}"


def invalid_rut():
    body = rng.randint(6_000_000, 25_000_000)
    wrong = next(d for d in "0123456789K" if d != rut_check_digit(body))
    return f"{body}-{wrong}"


def phone():
    return f"+56 9 {rng.randint(1000, 9999)} {rng.randint(1000, 9999)}"


def mail(n):
    return n.lower().split()[0].replace("í", "i").replace("á", "a") + "@example.test"


manifest = {}


def record(fname, valid=(), invalid=(), phones=()):
    manifest[fname] = {"valid_ruts": list(valid), "invalid_ruts": list(invalid), "phones": list(phones)}


def write(fname, text, **kw):
    (OUT / fname).write_text(text, encoding="utf-8")
    record(fname, **kw)


def main():
    OUT.mkdir(exist_ok=True)

    # 1-3 emails
    n, r, p = name(), valid_rut("dots"), phone()
    write("correo_01.txt", f"Asunto: Actualización de datos\n\nHola, soy {n}, mi RUT es {r} y mi celular {p}.\nPueden escribirme a {mail(n)}.\nSaludos.\n", valid=[r], phones=[p])
    n, r = name(), valid_rut("dash")
    write("correo_02.txt", f"Estimados:\n\nAdjunto cédula de identidad de {n}, RUN {r}.\nContacto: {mail(n)}, fono {phone()}.\n", valid=[r])
    bad, inv1, inv2 = invalid_rut(), f"FAC-{rng.randint(10_000_000, 99_999_999)}", rng.randint(100_000_000, 999_999_999)
    write("correo_03_falsos_positivos.txt", f"Factura N° {inv1} por $ {inv2:,}.\nOrden de compra {rng.randint(10000000, 99999999)}.\nRUT mal digitado: {bad}\n".replace(",", "."), invalid=[bad])

    # 4-5 licencias médicas
    for i in (1, 2):
        n, r = name(), valid_rut("dots")
        write(f"licencia_medica_{i:02d}.txt",
              f"LICENCIA MÉDICA N° {rng.randint(10**7, 10**8 - 1)}\nPaciente: {n}\nRUT: {r}\nDiagnóstico: Asma, CIE-10 J45.9\n"
              f"Previsión: {'Fonasa' if i == 1 else 'Isapre Colmena'}\nReposo: {rng.randint(3, 15)} días\nTeléfono: {phone()}\n", valid=[r])

    # 6-7 CSV
    for i, rows in ((1, 6), (2, 4)):
        valid, invalid = [], []
        path = OUT / f"planilla_{i:02d}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["nombre", "rut", "telefono", "email", "ficha"])
            for _ in range(rows):
                nm = name()
                if rng.random() < 0.8:
                    rr = valid_rut(rng.choice(["dots", "dash", "plain"]))
                    valid.append(rr)
                else:
                    rr = invalid_rut()
                    invalid.append(rr)
                w.writerow([nm, rr, phone(), mail(nm), f"F-{rng.randint(1000, 9999)}"])
        record(path.name, valid, invalid)

    # 8 ficha
    n, r = name(), valid_rut("dash")
    write("ficha_paciente_01.txt", f"FICHA CLÍNICA\nNombre: {n}\nRUT: {r}\nReceta: Salbutamol 100 mcg\nDiagnóstico: Hipertensión, CIE-10 I10.0\nContacto celular: {phone()}\n", valid=[r])

    # 9 PDF con texto
    n, r = name(), valid_rut("dots")
    pdf_text = [f"Certificado de atención", f"Paciente: {n}", f"RUT: {r}", f"Licencia médica por diagnóstico J45.9", f"Teléfono: {phone()}"]
    c = canvas.Canvas(str(OUT / "documento_texto_09.pdf"), pagesize=A4)
    y = 800
    for line in pdf_text:
        c.drawString(60, y, line)
        y -= 24
    c.save()
    record("documento_texto_09.pdf", valid=[r])

    # 10 PDF escaneado (solo imagen) + PNG
    n, r = name(), valid_rut("dots")
    lines = ["CERTIFICADO MEDICO", f"Paciente: {n}", f"RUT: {r}", "Diagnostico: Asma J45.9", f"Telefono: {phone()}"]
    FONTS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    font_path = next((f for f in FONTS if Path(f).exists()), None)
    font = ImageFont.truetype(font_path, 44) if font_path else ImageFont.load_default(44)
    img = Image.new("RGB", (1240, 700), "white")
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((70, 60 + i * 90), line, fill="black", font=font)
    img = img.rotate(0.6, fillcolor="white")
    img.save(OUT / "documento_escaneado_10.png")
    img.save(OUT / "documento_escaneado_10.pdf", "PDF", resolution=150)
    record("documento_escaneado_10.pdf", valid=[r])

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(manifest)} fixtures in {OUT}")


if __name__ == "__main__":
    main()
