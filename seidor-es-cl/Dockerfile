# Build from the repo root:  docker build -f seidor-es-cl/Dockerfile .
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 UV_PROJECT_ENVIRONMENT=/usr/local \
    NLP_CONF_FILE=/app/seidor-conf/nlp_es.yaml \
    ANALYZER_CONF_FILE=/app/seidor-conf/analyzer_es.yaml \
    RECOGNIZER_REGISTRY_CONF_FILE=/app/seidor-conf/recognizers_es.yaml \
    PYTHONPATH=/app:/app/seidor-es-cl \
    PORT=3000 WORKERS=1

WORKDIR /app
RUN apt-get update && apt-get install curl --no-install-recommends -y && rm -rf /var/lib/apt/lists/*

COPY presidio-analyzer/pyproject.toml presidio-analyzer/uv.lock /app/
RUN pip install uv==0.11.6 \
    && uv sync --locked --no-cache --no-default-groups --extra server --no-install-project

COPY presidio-analyzer/install_nlp_models.py /app/
COPY seidor-es-cl/conf /app/seidor-conf
RUN python install_nlp_models.py --conf_file ${NLP_CONF_FILE} --analyzer_conf_file ${ANALYZER_CONF_FILE}

COPY presidio-analyzer/ /app/
COPY seidor-es-cl/seidor_cl /app/seidor-es-cl/seidor_cl
RUN useradd -m -u 1001 presidio && chown -R presidio:presidio /app
USER 1001

EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=3s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1
CMD ["sh", "-c", "exec gunicorn --preload -w $WORKERS -b 0.0.0.0:$PORT --timeout 120 'seidor_cl.app:create_app()'"]
