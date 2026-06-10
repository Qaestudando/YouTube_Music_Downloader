import requests

MUSICBRAINZ_URL = "https://musicbrainz.org/ws/2"


def procurar_album(artista: str, musica: str):
    """
    Procura um álbum a partir do artista e da música.

    Retorna um dicionário:
    {
        "artist": "...",
        "album": "...",
        "year": "...",
        "tracks": [...]
    }

    ou None caso não encontre.
    """

    headers = {
        "User-Agent": "YoutubeMusicDownloader/1.0"
    }

    query = (
        f'recording:"{musica}" AND artist:"{artista}"'
    )

    try:

        resposta = requests.get(
            f"{MUSICBRAINZ_URL}/recording",
            params={
                "query": query,
                "fmt": "json"
            },
            headers=headers,
            timeout=15
        )

        resposta.raise_for_status()

        dados = resposta.json()

        gravacoes = dados.get("recordings", [])

        if not gravacoes:
            return None

        gravacao = gravacoes[0]

        releases = gravacao.get("releases", [])

        if not releases:
            return None

        release = releases[0]

        album = release.get("title", "Desconhecido")
        year = release.get("date", "")[:4]

        release_id = release.get("id")

        resposta = requests.get(
            f"{MUSICBRAINZ_URL}/release/{release_id}",
            params={
                "inc": "recordings",
                "fmt": "json"
            },
            headers=headers,
            timeout=15
        )

        resposta.raise_for_status()

        detalhes = resposta.json()

        tracks = []

        for media in detalhes.get("media", []):

            for faixa in media.get("tracks", []):

                nome = faixa.get("title")

                if nome:
                    tracks.append(nome)

        return {
            "artist": artista,
            "album": album,
            "year": year,
            "tracks": tracks
        }

    except Exception:

        return None