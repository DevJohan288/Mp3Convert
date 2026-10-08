"""Configuración central de la aplicación."""
import os
import tempfile


class Config:
    """Valores por defecto para correr la app en red local / Tailscale."""

    HOST = "0.0.0.0"
    PORT = 5000
    DEBUG = False

    DOWNLOAD_ROOT = os.path.join(tempfile.gettempdir(), "yt_downloader_app")

    # "%(artist,uploader,channel|Desconocido)s" prueba cada campo en orden
    # y usa el primero que exista; ".60s" trunca a 60 caracteres.
    OUTPUT_TEMPLATE = (
        "%(artist,uploader,channel|Desconocido).60s - %(track,title).80s.%(ext)s"
    )

    MP3_QUALITIES = ("128", "192", "320")
    MP4_QUALITIES = ("360", "480", "720", "1080")
    DEFAULT_MP3_QUALITY = "192"
    DEFAULT_MP4_QUALITY = "720"
