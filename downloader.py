import json
from pathlib import Path

from yt_dlp import YoutubeDL


class Downloader:
    def __init__(self):
        # Pasta base dos downloads
        self.base_dir = Path.home() / "Downloads" / "Musicas"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Arquivo de controle de downloads
        self.db_path = Path("downloads.json")

        if self.db_path.exists():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.baixados = json.load(f)
            except Exception:
                self.baixados = {}
        else:
            self.baixados = {}
    def baixar_album(self, artista, album, faixas, pesquisar_funcao):
    
# =========================
# Baixar todas as faixas de um álbum
# =========================
    

        pasta = f"{artista}/{album}"

        for faixa in faixas:

            consulta = f"{artista} {faixa}"

            resultado = pesquisar_funcao(consulta)

            if resultado is None:
                print(f"Não encontrado: {consulta}")
                continue

            if self.ja_baixado(resultado["id"]):
                print(f"Já baixado: {faixa}")
                continue

            try:
                self.baixar_audio(
                    resultado["id"],
                    pasta
                )

                self.marcar_baixado(
                    resultado["id"]
                )

            except Exception as erro:
                print(erro)

    def salvar_db(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(
                self.baixados,
                f,
                ensure_ascii=False,
                indent=2,
            )

    def ja_baixado(self, video_id: str) -> bool:
        return video_id in self.baixados

    def marcar_baixado(self, video_id: str):
        self.baixados[video_id] = True
        self.salvar_db()

    def baixar_audio(self, video_id: str, pasta: str = "Diversos"):
        """
        Baixa um vídeo do YouTube e converte para MP3.
        """

        destino = self.base_dir / pasta
        destino.mkdir(parents=True, exist_ok=True)

        url = f"https://www.youtube.com/watch?v={video_id}"

        opcoes = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "windowsfilenames": True,
            "ignoreerrors": True,
            "outtmpl": str(destino / "%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
        }

        with YoutubeDL(opcoes) as ydl:
            ydl.download([url])