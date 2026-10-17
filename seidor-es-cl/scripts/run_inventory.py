"""Run all fixtures through the analyzer (REST or in-process) and write a CSV inventory."""
import argparse
import csv
import sys
import time
from pathlib import Path

import fitz  # pymupdf
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def read_text(path: Path) -> str:
    if path.suffix == ".pdf":
        return "\n".join(page.get_text() for page in fitz.open(path))
    return path.read_text(encoding="utf-8")


def analyze_rest(url, text):
    r = requests.post(f"{url}/analyze", json={"text": text, "language": "es"}, timeout=120)
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:5002")
    ap.add_argument("--fixtures", default=str(ROOT / "fixtures"))
    ap.add_argument("--out", default=str(ROOT / "inventory.csv"))
    ap.add_argument("--repeat", type=int, default=1, help="repeat the corpus N times to time it")
    a = ap.parse_args()

    files = sorted(p for p in Path(a.fixtures).iterdir() if p.suffix in {".txt", ".csv", ".pdf"})
    rows, total_bytes, elapsed = [], 0, 0.0
    for rep in range(a.repeat):
        for f in files:
            text = read_text(f)
            if not text.strip():
                if rep == 0:
                    print(f"SKIP {f.name}: no text layer (needs OCR / image-redactor)")
                continue
            t0 = time.perf_counter()
            res = analyze_rest(a.url, text)
            elapsed += time.perf_counter() - t0
            total_bytes += len(text.encode("utf-8"))
            if rep == 0:
                for x in res:
                    rows.append([f.name, x["entity_type"], round(x["score"], 3), x["start"], x["end"], text[x["start"]:x["end"]]])
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["archivo", "tipo_entidad", "score", "inicio", "fin", "texto_detectado"])
        w.writerows(rows)
    mb = total_bytes / 1e6
    print(f"{len(rows)} detections -> {a.out}")
    print(f"throughput: {mb:.4f} MB in {elapsed:.1f}s = {mb / elapsed * 60:.2f} MB/min (text extracted, {a.repeat}x corpus)")


if __name__ == "__main__":
    main()
