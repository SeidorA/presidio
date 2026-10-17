# Presidio ES/CL — evaluación para data discovery (Ley 21.719)

Fork de `microsoft/presidio` con extensiones en `seidor-es-cl/` (rama `feature/es-cl`). **No se modificó el core de Presidio**: los recognizers y los entrypoints viven en el paquete `seidor_cl` y se inyectan al analyzer/image-redactor sin tocar su código.

## Cómo levantar todo

```bash
# 1) Servicios (analyzer ES+CL, anonymizer, image-redactor con OCR en español). Sin Ollama ni servicios externos.
docker compose -f seidor-es-cl/docker-compose.es-cl.yml up -d --build

# 2) Verificación
curl localhost:5001/health   # anonymizer
curl localhost:5002/health   # analyzer
curl localhost:5003/health   # image-redactor
curl localhost:5002/analyze -H 'content-type: application/json' \
  -d '{"text":"Mi RUT es 12.345.678-5, fono +56 9 8765 4321","language":"es"}'

# 3) Demo Streamlit (virtualenv local)
uv venv --python 3.12 .venv && . .venv/bin/activate
uv pip install -e "presidio-analyzer[server]" -e presidio-anonymizer -e presidio-image-redactor \
  pytest streamlit streamlit-tags st-annotated-text pandas python-dotenv reportlab pillow pymupdf
python -m spacy download es_core_news_lg
streamlit run seidor-es-cl/streamlit/app_es_cl.py --server.port 8501   # http://localhost:8501

# 4) Pruebas e inventario
python seidor-es-cl/scripts/generate_fixtures.py     # regenera fixtures sintéticos (seed fija)
cd seidor-es-cl && python -m pytest tests -q
python scripts/run_inventory.py --url http://localhost:5002   # -> inventory.csv
```

Puertos (verificados en `docker-compose.yml` y Dockerfiles): anonymizer 5001, analyzer 5002, image-redactor 5003 (el contenedor escucha en `PORT`, aquí 3000).
Apple Silicon: las imágenes se construyeron **nativas arm64**, sin `--platform`. Del `docker-compose.yml` upstream se construyeron anonymizer e image-redactor (con `REGISTRY_NAME=local IMAGE_PREFIX= TAG=:local`); el analyzer upstream no se levantó porque depende de un servicio Ollama que no necesitamos, por eso usamos un compose propio.

## Arquitectura

```
cliente ─► analyzer :5002  (Presidio Flask + spaCy es_core_news_lg + seidor_cl)
        ─► anonymizer :5001 (Presidio, sin cambios)
        ─► image-redactor :5003 (Tesseract spa + analyzer ES + seidor_cl)
Streamlit :8501 ─► librería in-process, o REST al analyzer
```

- `seidor_cl/cl_rut_recognizer.py` — `ClRutRecognizer` (`CL_RUT`): con/sin puntos y guion, DV módulo 11 (incl. K y 0), rango de cuerpo 1.000.000–99.999.999. DV inválido ⇒ descartado. Score por forma: con puntos 0.85, con guion 0.75, `…K` sin guion 0.3, solo dígitos 0.05 (sube a ~0.45 solo con contexto: RUT, RUN, rol único tributario, cédula de identidad).
- `cl_phone_recognizer.py` — `CL_PHONE_NUMBER` (+56 9 …, +56 2 …).
- `es_health_recognizer.py` — **EXPERIMENTAL**: `ES_HEALTH_TERM` (diagnóstico, licencia médica, receta, isapre, fonasa, ficha clínica) e `ICD10_CODE` (CIE-10 tipo J45.9).
- `seidor_cl/app.py` / `image_app.py` — reutilizan `Server` de Presidio y añaden los recognizers al registry.
- `conf/` — NLP spaCy es (`es_core_news_lg`), analyzer y registry en `es`.

## Qué funcionó

- 35 tests pytest pasan (RUT válidos/ inválidos/ K/ DV 0, falsos positivos tipo factura y montos, teléfono, CIE-10, términos de salud).
- RUT con puntos/guion detectados de forma fiable; RUT con DV mal digitado no se reporta; números de factura/orden no se marcan como RUT con score ≥ 0.4.
- Analyzer, anonymizer e image-redactor responden vía curl; anonymizer reemplaza `CL_RUT` correctamente.
- OCR en español sobre un escaneado sintético limpio (PNG/Arial 44 px): texto, RUT y teléfono leídos correctamente (incluyendo tildes con `-l spa`); redacción visual de nombre, RUT, CIE-10 y teléfono.

## Limitaciones encontradas

- **Falsos positivos de spaCy es**: `PERSON`/`LOCATION`/`ORGANIZATION` ruidosos en textos estructurados (p. ej. "Orden" → ORGANIZATION, "Teléfono" → LOCATION, `J45.9\nPrevisión:` → PERSON). Requiere umbral, allow-lists y/o un modelo NER afinado.
- **Doble detección de teléfono**: el recognizer genérico `PHONE_NUMBER` (score 0.4) coexiste con `CL_PHONE_NUMBER`; deduplicar por entidad en el consumidor.
- **Salud en español**: el recognizer es de palabras clave; detecta *términos*, no datos de salud de una persona. Alta tasa de FP/FN, sin contexto clínico real. Experimental.
- **Solo dígitos**: RUT sin separadores es indistinguible de otros números de 8–9 dígitos sin contexto (1 de cada 11 números aleatorios pasa el DV). Se mitiga con score bajo + contexto.
- **OCR**: probado solo con un escaneado sintético limpio; no representa escaneos reales (ruido, inclinación, baja resolución). El image-redactor opera sobre **imágenes**, no PDF: un PDF escaneado debe rasterizarse antes. En la redacción del teléfono quedó un fragmento sin cubrir (el bbox por token no cubre bien el `+56 9 …`).
- Los fixtures PDF/CSV se inventarían leyendo texto (PyMuPDF); el PDF escaneado no tiene capa de texto y se omite en el inventario (requiere OCR).
- Sin evaluación de precisión/recall sobre datos reales; los fixtures son 10 documentos sintéticos pequeños.

## Throughput (medido, orientativo)

Corpus: 10 fixtures sintéticos (~3,5 KB de texto en total), analyzer en Docker arm64, 1 worker gunicorn, CPU del Mac.

| Escenario | Resultado |
|---|---|
| Un request por documento, corpus repetido 20× (0,038 MB) | ~1,0 MB/min (dominado por latencia por request) |
| Batch de 40 textos en un solo request (0,071 MB) | ~2,3 MB/min |

Para extrapolar, estas cifras son **bajas y no representativas** de documentos grandes: el corpus es muy pequeño. Conclusión: con 1 worker y `es_core_news_lg` el orden de magnitud es de unos pocos MB/min por worker; para volúmenes reales hay que escalar workers (`WORKERS`, `N_PROCESS`) y medir con un corpus mayor.

## Notas

- La demo upstream (`docs/samples/python/streamlit`) está fijada a inglés (`lang_code: "en"` en `presidio_nlp_engine_config.py`) y arrastra torch/flair/stanza. Para no tocarla se creó `seidor-es-cl/streamlit/app_es_cl.py`.
- Todos los datos de `fixtures/` son inventados (RUTs generados por script). Nada sale de la máquina: sin LLM ni APIs externas.
