# Deck — Descargador de YouTube (MP3 / MP4)

Aplicación web local, construida con Flask, para descargar audio o video de
YouTube. Pensada para uso personal en tu propia red.

> Úsala solo con contenido que tengas derecho a descargar (tu propio
> contenido, música libre de derechos, licencias Creative Commons, etc.).
> Descargar contenido con derechos de autor sin permiso puede infringir los
> términos de YouTube y las leyes de copyright de tu país.

## Arquitectura

El proyecto sigue una separación por capas al estilo de una API pequeña en
producción, en vez de meter toda la lógica en un solo archivo:

```
yt-downloader/
├── run.py                        # Punto de entrada: arranca el servidor
├── app/
│   ├── __init__.py                # App factory (create_app)
│   ├── config.py                  # Config: constantes centralizadas
│   ├── routes.py                  # Blueprint: capa HTTP, delgada
│   ├── services/
│   │   ├── downloader.py          # YouTubeDownloader, YouTubeURLValidator
│   │   ├── models.py              # TrackInfo, DownloadResult (dataclasses)
│   │   └── exceptions.py          # Jerarquía de errores del dominio
│   ├── templates/index.html
│   └── static/{css,js}/
└── tests/
    └── test_validator.py          # Pruebas unitarias (pytest)
```

**Por qué está dividido así:**

- **`app/services/downloader.py`** — Toda la interacción con `yt-dlp` vive en
  la clase `YouTubeDownloader`. Es la única parte del proyecto que sabe cómo
  se arma un `outtmpl`, qué opciones necesita `ffmpeg`, etc. Si mañana se
  cambia de librería de descarga, solo se toca este archivo.
- **`app/services/exceptions.py`** — Errores propios (`InvalidURLError`,
  `ExtractionError`, `DownloadFailedError`) en vez de `Exception` genérica,
  para que `routes.py` pueda decidir el código HTTP correcto sin adivinar.
- **`app/services/models.py`** — `TrackInfo` y `DownloadResult` son
  `dataclasses` simples: le dan forma a los datos que cruzan entre capas.
- **`app/routes.py`** — Capa de presentación: traduce HTTP ↔ llamadas al
  servicio. No sabe nada de `yt-dlp` ni de archivos temporales.
- **`app/__init__.py`** — Usa el patrón *Application Factory*
  (`create_app()`), el estándar recomendado por Flask: permite crear la app
  con distinta configuración (por ejemplo, para tests) sin variables
  globales.

## Requisitos

1. **Python 3.9+**
2. **ffmpeg** — necesario para convertir a MP3 y unir audio/video en MP4.
   - **Windows**: `winget install ffmpeg` (o `instalar.bat` ya lo hace por ti)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Instalación y uso (Windows)

Doble clic en **`instalar.bat`** — revisa/instala Python y ffmpeg si faltan,
crea el entorno virtual e instala dependencias, todo automático. Luego doble
clic en **`iniciar.bat`** cada vez que quieras usar la app.

## Instalación manual (cualquier sistema)

```bash
python3 -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 run.py
```

Abre tu navegador en **http://localhost:5000**

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

## Acceso remoto (desde el celular, fuera de casa)

La app escucha en toda la red (`0.0.0.0`), no solo en `127.0.0.1`. Para
usarla desde tu celular estando fuera de casa, instala **Tailscale**
(https://tailscale.com) en tu PC y en tu teléfono con la misma cuenta — crea
una red privada entre tus propios dispositivos sin exponer nada al internet
público. Al iniciar `run.py` verás en la terminal la IP local y un
recordatorio de usar la IP de Tailscale (empieza con `100.`) desde fuera de
casa.

No se recomienda abrir el puerto en el router directamente hacia internet
(port forwarding): esta app no tiene login, así que cualquiera que
encontrara esa dirección podría usarla.

## Cómo se usa

1. Pega el enlace de un video de YouTube.
2. Pulsa **Buscar** — verás título, canal, miniatura y duración.
3. Elige **MP3** (128/192/320 kbps) o **MP4** (360p–1080p).
4. Pulsa **Descargar** — el archivo se nombra automáticamente como
   `Artista - Título.ext` y se guarda donde tu navegador guarda descargas.

## Notas técnicas

- Los archivos se descargan a una carpeta temporal del sistema y se borran
  automáticamente después de enviarse al navegador (`after_this_request`).
- Si `yt-dlp` deja de funcionar con algunos videos, YouTube probablemente
  cambió algo en su sitio; actualízalo con `pip install -U yt-dlp`.
