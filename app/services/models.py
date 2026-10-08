"""Modelos de datos simples (dataclasses) para el dominio de descargas."""
from dataclasses import dataclass


@dataclass
class TrackInfo:
    """Metadata de un video, lista para mostrarse en la interfaz."""

    title: str
    uploader: str
    thumbnail: str
    duration: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "uploader": self.uploader,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
        }


@dataclass
class DownloadResult:
    """Referencia al archivo ya descargado/convertido en disco."""

    file_path: str
    file_name: str
    job_dir: str
