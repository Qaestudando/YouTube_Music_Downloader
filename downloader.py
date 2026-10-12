import json
import re
import shutil
from pathlib import Path
from yt_dlp import YoutubeDL


def safe_name(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', str(value)).strip(' .')
    return value[:90] or 'Diversos'


class Downloader:
    def __init__(self):
        self.base_dir = Path.home() / 'Downloads' / 'Musicas'
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(__file__).resolve().parent / 'downloads.json'
        try:
            self.baixados = json.loads(self.db_path.read_text(encoding='utf-8')) if self.db_path.exists() else {}
        except (OSError, ValueError):
            self.baixados = {}

    def salvar_db(self):
        self.db_path.write_text(json.dumps(self.baixados, ensure_ascii=False, indent=2), encoding='utf-8')

    def ja_baixado(self, video_id):
        record = self.baixados.get(video_id)
        if isinstance(record, dict):
            return bool(record.get('path') and Path(record['path']).is_file())
        return bool(record)  # Compatibilidade com registros antigos

    def marcar_baixado(self, video_id, caminho=None):
        self.baixados[video_id] = {'path': str(caminho)} if caminho else True
        self.salvar_db()

    def baixar_audio(self, video_id, pasta='Diversos'):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            raise RuntimeError('FFmpeg e FFprobe não encontrados no PATH do Windows.')
        destino = self.base_dir.joinpath(*(safe_name(p) for p in str(pasta).replace('\\', '/').split('/') if p and p != '.'))
        destino.mkdir(parents=True, exist_ok=True)
        url = f'https://www.youtube.com/watch?v={video_id}'
        opcoes = {
            'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True,
            'noplaylist': True, 'windowsfilenames': True,
            'outtmpl': str(destino / '%(title).150s [%(id)s].%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}],
        }
        with YoutubeDL(opcoes) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                raise RuntimeError('O YouTube não retornou dados do arquivo.')
            caminho = Path(ydl.prepare_filename(info)).with_suffix('.mp3')
        if not caminho.is_file():
            raise RuntimeError(f'Conversão não produziu MP3: {caminho}')
        self.marcar_baixado(video_id, caminho)
        return caminho

    def baixar_album(self, artista, album, faixas, pesquisar_funcao, callback=None, cancelado=None):
        for faixa in faixas:
            if cancelado and cancelado():
                break
            try:
                resultado = pesquisar_funcao(f'{artista} {faixa}')
                if not resultado:
                    if callback: callback(f'Não encontrado: {faixa}')
                    continue
                if self.ja_baixado(resultado['id']):
                    if callback: callback(f'Já baixado: {faixa}')
                    continue
                caminho = self.baixar_audio(resultado['id'], f'{artista}/{album}')
                if callback: callback(f'Concluído: {caminho.name}')
            except Exception as erro:
                if callback: callback(f'Erro em {faixa}: {erro}')
