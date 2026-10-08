"""Fábrica de la aplicación: construye y conecta las piezas (patrón
Application Factory), en vez de tener un objeto Flask global a nivel de
módulo. Facilita hacer pruebas con distintas configuraciones."""
from flask import Flask

from .config import Config
from .routes import bp
from .services import YouTubeDownloader


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    downloader = YouTubeDownloader(
        download_root=app.config["DOWNLOAD_ROOT"],
        output_template=app.config["OUTPUT_TEMPLATE"],
    )
    app.extensions["downloader"] = downloader

    app.register_blueprint(bp)

    return app
