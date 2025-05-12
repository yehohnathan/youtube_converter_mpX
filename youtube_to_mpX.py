"""
Descargador express para mi mamá: (libertad de usar a lo que quieran)
- Pide el enlace de YouTube
- Deja escoger mp3 o mp4
- Permite elegir resolución o bitrate
- Se asegura de que exista FFmpeg
- No me demanden porfa
"""
# ================================ LIBRERÍAS ================================ #
import sys
import subprocess
from shutil import which
from yt_dlp import YoutubeDL

# ================================ FUNCIONES ================================ #
MIN_HEIGHT = 143    # Resolución mínima aceptada >= 144p


def ensure_ffmpeg() -> str:
    """
    Verifica si FFmpeg está instalado.
    Si no está, lo instala calladito con imageio-ffmpeg.
    Devuelve la ruta al ejecutable.
    """
    path = which("ffmpeg")
    if path:
        return path

    try:
        import imageio_ffmpeg as iio  # noqa: WPS433
        return iio.get_ffmpeg_exe()
    except ImportError:
        subprocess.check_call(  # noqa: S603, S607
            [sys.executable, "-m", "pip", "install", "--quiet",
             "imageio-ffmpeg"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        import imageio_ffmpeg as iio  # noqa: WPS433
        return iio.get_ffmpeg_exe()


def fetch_video_qualities(url: str) -> list[int]:
    """
    Devuelve las alturas disponibles (en píxeles) para un vídeo.
    Solo incluye resoluciones superiores a MIN_HEIGHT.
    """
    with YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)

    return sorted({
        f['height'] for f in info.get('formats', [])
        if f.get('height') and f['height'] >= MIN_HEIGHT
    })


def ask_url() -> str:
    """Pregunta la URL hasta que empiece con http(s)."""
    url = input("1. Link de YouTube: ").strip()
    while not url.startswith(("http://", "https://")):
        url = input("   URL no válida. Ingresa el link completo: ").strip()
    return url


def ask_format() -> tuple[str, bool]:
    """Pregunta si quiere mp3 o mp4. Devuelve extensión y flag de audio."""
    print("\n2. Formato de salida:\n  1. mp3 (audio)\n  2. mp4 (vídeo)")
    choice = ""
    while choice not in ("1", "2"):
        choice = input("Selecciona 1 o 2: ").strip()
    ext = "mp3" if choice == "1" else "mp4"
    return ext, ext == "mp3"


def ask_audio_quality() -> str:
    """Pregunta el bitrate (kbps) para mp3."""
    audio_q = {"1": "64", "2": "128", "3": "192", "4": "256", "5": "320"}
    print("\nCalidades de audio (kbps):")
    for k, v in audio_q.items():
        print(f"  {k}. {v}")
    sel = ""
    while sel not in audio_q:
        sel = input("3. Selecciona calidad: ").strip()
    return audio_q[sel]


def ask_video_quality(url: str) -> str:
    """Pregunta la resolución para mp4."""
    print("\nObteniendo resoluciones disponibles…")
    resolutions = fetch_video_qualities(url)
    if not resolutions:
        print("⚠️  No hay resoluciones >360p. Abortando.")
        sys.exit(1)

    print("\nResoluciones de vídeo disponibles:")
    video_q = {str(i + 1): str(r) for i, r in enumerate(resolutions)}
    for k, r in video_q.items():
        print(f"  {k}. {r}p")

    sel = ""
    while sel not in video_q:
        sel = input("3. Selecciona resolución: ").strip()
    return video_q[sel]


def build_ydl_opts(ext: str, quality: str, is_audio: bool,
                   outtmpl: str, ffmpeg: str) -> dict:
    """Arma las opciones para yt-dlp según el formato elegido."""
    opts: dict = {
        "outtmpl": outtmpl,
        "ffmpeg_location": ffmpeg,
        "ffprobe_location": ffmpeg,
    }

    if is_audio:
        opts.update({
            "format": "bestaudio",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": ext,
                "preferredquality": quality,
            }],
        })
    else:
        # Fuerza un MP4 con vídeo ≤ quality y audio AAC
        opts["format"] = (
            f"bestvideo[height>={MIN_HEIGHT}][height<={quality}]"
            f"+bestaudio[ext=m4a]/"
            f"best[ext=mp4][height>={MIN_HEIGHT}]"
        )
        opts["merge_output_format"] = "mp4"

    return opts


def main() -> None:
    """Función principal: orquesta la fiesta de descargas."""
    url = ask_url()
    ext, is_audio = ask_format()

    quality = (
        ask_audio_quality() if is_audio else ask_video_quality(url)
    )

    nombre = input(
        "\n4. Nombre de salida (sin extensión): ").strip() or "output"
    outtmpl = f"{nombre}.%(ext)s"
    ffmpeg = ensure_ffmpeg()
    ydl_opts = build_ydl_opts(ext, quality, is_audio, outtmpl, ffmpeg)

    print("\n⬇️  Iniciando descarga…\n")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n✅ ¡Descarga completada! → {nombre}.{ext}")
    except Exception as exc:  # noqa: BLE001
        print(f"\n❌ Error durante la descarga: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Cancelado por el usuario.")
        sys.exit(0)
