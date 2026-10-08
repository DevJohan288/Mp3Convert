"""Servicio de descargas: encapsula toda la interacción con yt-dlp.

Dos clases con responsabilidad única:
- YouTubeURLValidator: sabe reconocer un enlace de YouTube válido.
- YouTubeDownloader: sabe consultar info y descargar/convertir un video.
Las rutas de Flask (app/routes.py) solo llaman a estas clases; no conocen
nada de yt-dlp ni del sistema de archivos.
"""
import os
import re
import shutil
import uuid

import yt_dlp

from .exceptions import DownloadFailedError, ExtractionError, InvalidURLError
from .models import DownloadResult, TrackInfo


class YouTubeURLValidator:
    """Valida que una cadena sea un enlace de YouTube soportado."""

    _PATTERN = re.compile(
        r"^(https?://)?(www\.)?(m\.)?"
        r"(youtube\.com/watch\?v=|youtube\.com/shorts/|youtu\.be/)[\w-]+"
    )

    @classmethod
    def is_valid(cls, url: str) -> bool:
        return bool(url) and bool(cls._PATTERN.match(url.strip()))


class YouTubeDownloader:
    """Punto único de acceso a yt-dlp: consultar metadata y descargar."""

    def __init__(self, download_root: str, output_template: str):
        self.download_root = download_root
        self.output_template = output_template
        os.makedirs(self.download_root, exist_ok=True)

    # ------------------------------------------------------------------ #
    # API pública
    # ------------------------------------------------------------------ #

    def get_info(self, url: str) -> TrackInfo:
        """Consulta metadata del video sin descargarlo."""
        self._validate_url(url)

        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as exc:
            raise ExtractionError(
                "No se pudo leer ese video. Revisa el enlace e intenta de nuevo."
            ) from exc

        return self._to_track_info(info)

    def download(self, url: str, fmt: str, quality: str) -> DownloadResult:
        """Descarga y convierte el video; devuelve la ruta del archivo final."""
        self._validate_url(url)

        if fmt not in ("mp3", "mp4"):
            raise DownloadFailedError("Formato no soportado.")

        job_dir = self._new_job_dir()
        opts = self._build_ydl_options(job_dir, fmt, quality)

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as exc:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise DownloadFailedError(f"No se pudo descargar ese video: {exc}") from exc

        return self._collect_result(job_dir)

    def cleanup(self, result: DownloadResult) -> None:
        """Borra la carpeta temporal de un trabajo ya enviado al navegador."""
        shutil.rmtree(result.job_dir, ignore_errors=True)

    # ------------------------------------------------------------------ #
    # Helpers privados
    # ------------------------------------------------------------------ #

    def _validate_url(self, url: str) -> None:
        if not YouTubeURLValidator.is_valid(url):
            raise InvalidURLError("Ese enlace no parece ser un video válido de YouTube.")

    def _new_job_dir(self) -> str:
        job_dir = os.path.join(self.download_root, uuid.uuid4().hex)
        os.makedirs(job_dir, exist_ok=True)
        return job_dir

    def _build_ydl_options(self, job_dir: str, fmt: str, quality: str) -> dict:
        outtmpl = os.path.join(job_dir, self.output_template)
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "outtmpl": outtmpl,
        }

        if fmt == "mp3":
            options.update(self._mp3_options(quality))
        else:
            options.update(self._mp4_options(quality))

        return options

    @staticmethod
    def _mp3_options(quality: str) -> dict:
        preferred_quality = quality if quality in ("128", "192", "320") else "192"
        return {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": preferred_quality,
            }],
        }

    @staticmethod
    def _mp4_options(quality: str) -> dict:
        height = quality if quality in ("360", "480", "720", "1080") else "720"
        return {
            "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            "merge_output_format": "mp4",
        }

    @staticmethod
    def _collect_result(job_dir: str) -> DownloadResult:
        files = [f for f in os.listdir(job_dir) if not f.endswith((".part", ".ytdl"))]
        if not files:
            shutil.rmtree(job_dir, ignore_errors=True)
            raise DownloadFailedError("No se generó ningún archivo.")

        file_name = files[0]
        return DownloadResult(
            file_path=os.path.join(job_dir, file_name),
            file_name=file_name,
            job_dir=job_dir,
        )

    @staticmethod
    def _to_track_info(info: dict) -> TrackInfo:
        duration = int(info.get("duration") or 0)
        minutes, seconds = divmod(duration, 60)
        return TrackInfo(
            title=info.get("title", "Sin título"),
            uploader=info.get("uploader", "Desconocido"),
            thumbnail=info.get("thumbnail", ""),
            duration=f"{minutes:02d}:{seconds:02d}",
        )
