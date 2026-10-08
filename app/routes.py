"""Rutas HTTP. No conocen yt-dlp ni el sistema de archivos directamente:
todo el trabajo se delega a YouTubeDownloader (ver app/services)."""
from flask import (
    Blueprint,
    after_this_request,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
)

from .services.exceptions import DownloaderError, InvalidURLError

bp = Blueprint("main", __name__)


def _downloader():
    return current_app.extensions["downloader"]


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/api/info", methods=["POST"])
def info():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    try:
        track = _downloader().get_info(url)
    except InvalidURLError as exc:
        return jsonify({"error": str(exc)}), 400
    except DownloaderError as exc:
        current_app.logger.warning("Error al leer info: %s", exc)
        return jsonify({"error": str(exc)}), 400

    return jsonify(track.to_dict())


@bp.route("/api/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    fmt = data.get("format", "mp3")
    quality = str(data.get("quality", "192"))

    downloader = _downloader()

    try:
        result = downloader.download(url, fmt, quality)
    except InvalidURLError as exc:
        return jsonify({"error": str(exc)}), 400
    except DownloaderError as exc:
        current_app.logger.warning("Error al descargar: %s", exc)
        return jsonify({"error": str(exc)}), 500

    @after_this_request
    def cleanup(response):
        downloader.cleanup(result)
        return response

    return send_file(result.file_path, as_attachment=True, download_name=result.file_name)
