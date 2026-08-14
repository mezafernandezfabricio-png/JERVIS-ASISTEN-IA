import yt_dlp
import os

def youtube_downloader(parameters: dict, player=None):
    url = parameters.get("url")
    if not url:
        return "Error: No se proporcionó la URL del video."

    try:
        # Define options as requested: format best, no merge
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(os.path.expanduser('~'), 'Desktop', '%(title)s.%(ext)s'),
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"Descarga completada. El video se ha guardado en el escritorio."
    except Exception as e:
        return f"Error durante la descarga: {str(e)}"