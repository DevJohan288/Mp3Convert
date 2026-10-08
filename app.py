import os
import re
import shutil
import socket
import tempfile
import traceback
import uuid

from flask import Flask, request, jsonify, send_file, render_template, after_this_request
import yt_dlp

app = Flask(__name__)

DOWNLOAD_ROOT = os.path.join(tempfile.gettempdir(), "yt_downloader_app")
os.makedirs(DOWNLOAD_ROOT, exist_ok=True)

YOUTUBE_URL_RE = re.compile(
    r"^(https?://)?(www\.)?(m\.)?(youtube\.com/watch\?v=|youtube\.com/shorts/|youtu\.be/)[\w-]+"
)


def is_valid_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_URL_RE.match(url.strip()))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Ese enlace no parece ser un video válido de YouTube."}), 400

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        print("\n--- ERROR AL LEER INFO ---")
        traceback.print_exc()
        print("--------------------------\n")
        return jsonify({"error": f"No se pudo leer ese video: {exc}"}), 400

    duration = int(info.get("duration") or 0)
    minutes, seconds = divmod(duration, 60)

    return jsonify({
        "title": info.get("title", "Sin título"),
        "uploader": info.get("uploader", "Desconocido"),
        "thumbnail": info.get("thumbnail", ""),
        "duration": f"{minutes:02d}:{seconds:02d}",
    })


@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    fmt = data.get("format", "mp3")
    quality = str(data.get("quality", "192"))

    if not url or not is_valid_youtube_url(url):
        return jsonify({"error": "Ese enlace no parece ser un video válido de YouTube."}), 400

    if fmt not in ("mp3", "mp4"):
        return jsonify({"error": "Formato no soportado."}), 400

    job_id = uuid.uuid4().hex
    job_dir = os.path.join(DOWNLOAD_ROOT, job_id)
    os.makedirs(job_dir, exist_ok=True)

    outtmpl = os.path.join(
        job_dir, "%(artist,uploader,channel|Desconocido).60s - %(track,title).80s.%(ext)s"
    )

    if fmt == "mp3":
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality if quality in ("128", "192", "320") else "192",
            }],
        }
    else:
        height = quality if quality in ("360", "480", "720", "1080") else "720"
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            "outtmpl": outtmpl,
            "merge_output_format": "mp4",
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as exc:
        print("\n--- ERROR AL DESCARGAR ---")
        traceback.print_exc()
        print("--------------------------\n")
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"error": f"No se pudo descargar ese video: {exc}"}), 500

    files = [f for f in os.listdir(job_dir) if not f.endswith((".part", ".ytdl"))]
    if not files:
        shutil.rmtree(job_dir, ignore_errors=True)
        return jsonify({"error": "No se generó ningún archivo."}), 500

    result_name = files[0]
    result_path = os.path.join(job_dir, result_name)

    @after_this_request
    def cleanup(response):
        try:
            shutil.rmtree(job_dir, ignore_errors=True)
        except Exception:
            pass
        return response

    return send_file(result_path, as_attachment=True, download_name=result_name)


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        print("\n*** AVISO: no se encontro 'ffmpeg' en el PATH. ***")
        print("*** La conversion a MP3/MP4 va a fallar hasta que lo instales. ***\n")

    local_ip = get_local_ip()
    print("\n============================================")
    print("  Deck esta corriendo.")
    print(f"  En esta PC:        http://127.0.0.1:5000")
    print(f"  En tu red local:   http://{local_ip}:5000")
    print("  Desde otro lugar:  usa la IP que te de Tailscale")
    print("============================================\n")

    app.run(host="0.0.0.0", port=5000, debug=False)
