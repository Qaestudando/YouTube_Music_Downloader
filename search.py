from yt_dlp import YoutubeDL

# Quantidade máxima de resultados exibidos
SEARCH_LIMIT = 50
from yt_dlp import YoutubeDL

def pesquisar_primeiro_resultado(consulta: str):
    """
    Retorna o primeiro resultado do YouTube para uma consulta.
    """

    opcoes = {
        "quiet": True,
        "extract_flat": True,
        "ignoreerrors": True,
    }

    with YoutubeDL(opcoes) as ydl:
        dados = ydl.extract_info(
            f"ytsearch1:{consulta}",
            download=False
        )

    entradas = dados.get("entries", [])

    if not entradas:
        return None

    item = entradas[0]

    return {
        "id": item.get("id"),
        "title": item.get("title"),
        "channel": item.get("channel") or item.get("uploader") or ""
    }

def pesquisar(termo: str) -> list:
    """
    Pesquisa vídeos no YouTube e retorna uma lista simplificada.

    Retorno:
    [
        {
            "id": "...",
            "title": "...",
            "channel": "..."
        }
    ]
    """

    opcoes = {
        "quiet": True,
        "extract_flat": True,
        "ignoreerrors": True,
        "skip_download": True,
        "playlist_items": f"1-{SEARCH_LIMIT}",
    }

    resultados = []

    with YoutubeDL(opcoes) as ydl:
        resposta = ydl.extract_info(
            f"ytsearch{SEARCH_LIMIT}:{termo}",
            download=False
        )

    if not resposta:
        return resultados

    for item in resposta.get("entries", []):

        if not item:
            continue

        video_id = item.get("id")

        if not video_id:
            continue

        resultados.append({
            "id": video_id,
            "title": item.get("title", "Sem título"),
            "channel": (
                item.get("channel")
                or item.get("uploader")
                or "Canal desconhecido"
            )
        })

    return resultados


if __name__ == "__main__":
    termo = input("Pesquisar: ")

    resultados = pesquisar(termo)

    print(f"\nForam encontrados {len(resultados)} resultados:\n")

    for indice, video in enumerate(resultados, start=1):
        print(
            f"{indice:02d}. "
            f"{video['title']} "
            f"({video['channel']})"
        )