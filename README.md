# Deck — Descargador de YouTube (MP3 / MP4)

Aplicación web local construida con Flask para consultar videos de YouTube y
descargar su audio como MP3 o el video como MP4. También se puede usar desde
otros dispositivos de la red local.

> Úsala solo con contenido que tengas derecho a descargar, como contenido
> propio o con una licencia que lo permita. Descargar contenido protegido sin
> autorización puede infringir los términos de YouTube y las leyes de tu país.

## Requisitos

- Python 3.9 o posterior.
- **ffmpeg**, necesario para convertir audio a MP3 y combinar audio y video en
  MP4.
  - **Windows:** `instalar.bat` intenta instalarlo con `winget`; también puedes
    instalarlo con `winget install --id Gyan.FFmpeg -e`.
  - **macOS:** `brew install ffmpeg`.
  - **Ubuntu/Debian:** `sudo apt install ffmpeg`.

## Instalación y uso en Windows

1. Ejecuta **`instalar.bat`**. Comprueba Python y ffmpeg, intenta instalarlos
   con `winget` si faltan, crea `venv` e instala las dependencias.
2. Si acabas de instalar Python o ffmpeg, abre una terminal nueva y vuelve a
   ejecutar `instalar.bat` para que Windows actualice el `PATH`.
3. Ejecuta **`iniciar.bat`** cada vez que quieras iniciar la aplicación.
4. Abre **http://127.0.0.1:5000** en el navegador.

## Instalación manual

```bash
python -m venv venv
```

Activa el entorno virtual:

```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Instala las dependencias e inicia la aplicación:

```bash
python -m pip install -r requirements.txt
python run.py
```

La aplicación muestra en la terminal las direcciones disponibles para la PC y
la red local.

## Cómo se usa

1. Pega el enlace de un video de YouTube y pulsa **Buscar**.
2. Revisa el título, el canal, la miniatura y la duración.
3. Elige MP3 (128, 192 o 320 kbps) o MP4 (hasta 360p, 480p, 720p o 1080p).
4. Pulsa **Descargar**. El archivo se guarda en la carpeta de descargas del
   navegador.

## Estructura del proyecto

```text
run.py                       # Punto de entrada usado por los scripts de Windows
app/
  __init__.py                # Fábrica de la aplicación Flask
  config.py                 # Configuración, formatos y calidades
  routes.py                 # Rutas HTTP
  services/
    downloader.py            # Integración con yt-dlp
    exceptions.py            # Errores del dominio
    models.py                # Modelos de datos
  templates/
  static/
tests/
  test_validator.py          # Pruebas del validador de URLs
instalar.bat                 # Instalación automatizada en Windows
iniciar.bat                  # Inicio automatizado en Windows
requirements.txt             # Dependencias de ejecución
requirements-dev.txt         # Dependencias para pruebas
```

La aplicación modular que se inicia con `run.py` está dentro de `app/`: las
rutas delegan las descargas al servicio `YouTubeDownloader`, y la configuración
se concentra en `app/config.py`. El archivo raíz `app.py` y las carpetas raíz
`templates/` y `static/` también están presentes en el repositorio, pero los
scripts de Windows no los usan.

## Pruebas

Con las dependencias de ejecución instaladas, instala las dependencias de
desarrollo y ejecuta pytest:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Acceso desde otros dispositivos

El servidor escucha en la red local (`0.0.0.0`). Para acceder desde el celular
estando fuera de casa, puedes instalar **Tailscale** en la PC y el teléfono y
usar la IP de Tailscale de la PC (normalmente empieza por `100.`). La terminal
recuerda que debes usar esa IP para conectarte desde fuera de casa.

No se recomienda redirigir el puerto del router directamente a internet
(port forwarding): la aplicación no tiene inicio de sesión.

## Notas

- Las descargas se guardan temporalmente y se eliminan después de enviarse al
  navegador.
- Si `yt-dlp` deja de funcionar con algunos videos, actualízalo dentro del
  entorno virtual con `python -m pip install -U yt-dlp`.
