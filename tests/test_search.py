import pytest

from trackhunter.search import score_candidate_text


def test_nao_aceitar_titulo_parecido() -> None:
    score = score_candidate_text(
        "Anyma - Pictures Of You",
        "Anyma - Pictures Of Me",
        "MP3",
        "mp3",
    )

    assert score == 0


@pytest.mark.parametrize(
    ("track", "raw_text", "button_text", "download_format", "should_match"),
    [
        ("Anyma - Pictures Of You", "Anyma - Pictures Of You", "MP3", "mp3", True),
        ("Anyma - Acao Rapida", "Anyma - Ação Rápida", "MP3", "mp3", True),
        ("Anyma - Pictures Of You", "Other Artist - Pictures Of You", "MP3", "mp3", False),
        ("Anyma - Pictures Of You (Extended Remix)", "Anyma - Pictures Of You Extended Remix", "MP3", "mp3", True),
        ("Anyma - Pictures Of You (Extended Remix)", "Anyma - Pictures Of You Radio Edit", "MP3", "mp3", False),
        ("Anyma - Pictures Of You", "Anyma Pictures You Of", "MP3", "mp3", False),
        ("A B - Go", "A B - Go", "MP3", "mp3", True),
        ("Anyma & Chris Avantgarde - Eternity", "Anyma Chris Avantgarde Eternity", "MP3", "mp3", True),
        ("Anyma feat John - Pictures", "Anyma ft John Pictures", "MP3", "mp3", True),
        ("Guns N' Roses - Don't Cry", "Guns N Roses Dont Cry", "MP3", "mp3", True),
        ("Anyma - Pictures Of You", "Anyma - Pictures Of You", "AIFF", "aiff", True),
        ("Anyma - Pictures Of You", "Anyma - Pictures Of You", "AIFF", "mp3", True),
        ("Anyma - Pictures Of You", "Anyma - Pictures Of You Extended Remix", "MP3", "mp3", True),
        ("Anyma - Pictures Of You (Extended Remix)", "Anyma - Pictures Of You", "MP3", "mp3", False),
        ("Anyma - Pictures Of You", "Anyma - Pictures Of Us", "MP3", "mp3", False),
    ],
)
def test_score_candidate_text_cases(
    track: str,
    raw_text: str,
    button_text: str,
    download_format: str,
    should_match: bool,
) -> None:
    score = score_candidate_text(track, raw_text, button_text, download_format)

    if should_match:
        assert score >= 80
    else:
        assert score == 0


def test_preferred_format_button_scores_higher() -> None:
    mp3_score = score_candidate_text("Anyma - Pictures Of You", "Anyma - Pictures Of You", "MP3", "mp3")
    aiff_button_score = score_candidate_text("Anyma - Pictures Of You", "Anyma - Pictures Of You", "AIFF", "mp3")

    assert mp3_score > aiff_button_score
