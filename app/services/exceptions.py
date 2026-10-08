"""Excepciones del servicio de descargas.

Se separan en jerarquía propia para que las rutas puedan decidir el código
HTTP correcto según el tipo de fallo, sin tener que inspeccionar texto.
"""


class DownloaderError(Exception):
    """Error base para cualquier fallo del servicio de descargas."""


class InvalidURLError(DownloaderError):
    """La URL proporcionada no es un enlace de YouTube soportado."""


class ExtractionError(DownloaderError):
    """No se pudo leer la información (metadata) del video."""


class DownloadFailedError(DownloaderError):
    """No se pudo completar la descarga o la conversión."""
