import pytest
from intelli3text.lid.fasttext_lid import FastTextLID

PT = "Este é um parágrafo de teste em português com acentuação."
EN = "This is a short English paragraph used for language identification."
MIX = "Resumo. Este estudo... Abstract. This paper..."

def test_pt_confident():
    lid = FastTextLID(max_chars=512)
    lang, score = lid.detect(PT)
    assert lang.startswith("pt"), (lang, score)
    assert score > 0.80

def test_en_confident():
    lid = FastTextLID(max_chars=512)
    lang, score = lid.detect(EN)
    assert lang.startswith("en"), (lang, score)
    assert score > 0.80

def test_mix_lower_confidence():
    lid = FastTextLID(max_chars=512)
    lang, score = lid.detect(MIX)
    assert score < 0.80  # deve cair pois é misto
