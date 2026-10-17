"""Dockerized analyzer entrypoint: Presidio's Flask server + Chile recognizers."""
from app import Server  # presidio-analyzer/app.py, unmodified

from seidor_cl import register_cl_recognizers


def create_app():  # noqa: D103
    server = Server()
    register_cl_recognizers(server.engine.registry, "es")
    return server.app
