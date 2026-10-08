"""Punto de entrada. Uso: python run.py"""
import shutil
import socket

from app import create_app

app = create_app()


def get_local_ip() -> str:
    """Detecta la IP de esta PC en la red local (para acceder desde el cel)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def warn_if_ffmpeg_missing() -> None:
    if shutil.which("ffmpeg") is None:
        print("\n*** AVISO: no se encontro 'ffmpeg' en el PATH. ***")
        print("*** La conversion a MP3/MP4 va a fallar hasta que lo instales. ***\n")


if __name__ == "__main__":
    warn_if_ffmpeg_missing()
    local_ip = get_local_ip()

    print("\n============================================")
    print("  Deck esta corriendo.")
    print("  En esta PC:        http://127.0.0.1:5000")
    print(f"  En tu red local:   http://{local_ip}:5000")
    print("  Desde otro lugar:  usa la IP que te de Tailscale")
    print("============================================\n")

    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
