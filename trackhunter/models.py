from dataclasses import dataclass


@dataclass
class TrackResult:
    # Faixa original lida do arquivo de tracklist.
    track: str
    # Resultado final: baixada | ja_baixada | nao_encontrada | erro.
    status: str
    # Mensagem curta explicando o que aconteceu com a faixa.
    detail: str
    # Nome do arquivo baixado (quando houver download).
    file_name: str = ""


@dataclass
class TrackParts:
    # Artista extraido da string "artista - titulo (versao)".
    artist: str
    # Titulo da musica sem artista/versao.
    title: str
    # Versao/remix entre parenteses, quando existir.
    version: str
