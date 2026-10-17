"""Streamlit demo: Presidio in Spanish + Chile recognizers (local only)."""
import sys
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from annotated_text import annotated_text
from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seidor_cl.engine import build_analyzer  # noqa: E402

st.set_page_config(page_title="Presidio ES/CL", layout="wide")
st.title("Presidio · Español + Chile (Ley 21.719)")
st.caption("Todo corre local. Recognizers de salud: EXPERIMENTALES.")

DEFAULT = (
    "Paciente: Camila Rojas Soto, RUT 12.345.678-5, celular +56 9 8765 4321.\n"
    "Diagnóstico CIE-10 J45.9, licencia médica por Fonasa. Factura N° 48201937."
)


@st.cache_resource
def get_engine():
    return build_analyzer()


mode = st.sidebar.radio("Motor", ["Librería (in-process)", "REST analyzer dockerizado"])
url = st.sidebar.text_input("URL analyzer", "http://localhost:5002")
threshold = st.sidebar.slider("Score mínimo", 0.0, 1.0, 0.4, 0.05)
operator = st.sidebar.selectbox("Anonimización", ["replace", "redact", "mask", "hash"])
text = st.text_area("Texto", DEFAULT, height=180)

if st.button("Analizar", type="primary"):
    if mode.startswith("Lib"):
        results = get_engine().analyze(text, language="es", score_threshold=threshold)
        items = [r.to_dict() for r in results]
    else:
        resp = requests.post(f"{url}/analyze", json={"text": text, "language": "es", "score_threshold": threshold}, timeout=60)
        resp.raise_for_status()
        items = resp.json()
    items = sorted(items, key=lambda x: x["start"])
    parts, pos = [], 0
    for it in items:
        if it["start"] < pos:
            continue
        parts += [text[pos:it["start"]], (text[it["start"]:it["end"]], it["entity_type"])]
        pos = it["end"]
    parts.append(text[pos:])
    annotated_text(*parts)
    st.dataframe(pd.DataFrame([{**i, "texto": text[i["start"]:i["end"]]} for i in items]))
    rr = [RecognizerResult(i["entity_type"], i["start"], i["end"], i["score"]) for i in items]
    ops = {"DEFAULT": OperatorConfig(operator, {"masking_char": "*", "chars_to_mask": 20, "from_end": False} if operator == "mask" else {})}
    st.code(AnonymizerEngine().anonymize(text, rr, ops).text)
