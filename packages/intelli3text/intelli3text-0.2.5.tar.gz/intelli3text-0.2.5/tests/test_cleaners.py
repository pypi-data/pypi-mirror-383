import pytest

from intelli3text.cleaners.chain import CleanerChain
from intelli3text.cleaners.pdf_linebreaks import PDFLineBreaksCleaner


def test_cleaners_chain_basic():
    chain = CleanerChain.from_names(["ftfy", "clean_text"])
    text = "Text with URL http://example.com  and   extra   spaces"
    out = chain.apply(text)
    assert isinstance(out, str)
    # clean-text removes URLs (replaced by a space, then normalized)
    assert "http://example.com" not in out
    # Collapsed whitespace
    assert "  " not in out


def test_cleaners_chain_order_matters():
    # Ensure from_names respects order and does not blow up
    chain_a = CleanerChain.from_names(["ftfy", "clean_text", "pdf_breaks"])
    chain_b = CleanerChain.from_names(["pdf_breaks", "ftfy", "clean_text"])

    sample = "Hyphen-\n ation and URL http://example.com"

    out_a = chain_a.apply(sample)
    out_b = chain_b.apply(sample)

    assert isinstance(out_a, str) and isinstance(out_b, str)
    # Both should remove URL
    assert "http://example.com" not in out_a
    assert "http://example.com" not in out_b
    # Both should de-hyphenate across line breaks
    assert "Hyphen- ation" not in out_a
    assert "Hyphen- ation" not in out_b
    assert "Hyphenation" in out_a or "Hyphenation" in out_b


def test_cleaners_chain_apply_paragraph():
    chain = CleanerChain.from_names(["clean_text"])
    para = "See contact me at mail@example.com and visit https://example.org"
    out = chain.apply_paragraph(para)
    assert "mail@example.com" not in out
    assert "https://example.org" not in out


def test_pdf_linebreaks_cleaner_hyphenation():
    c = PDFLineBreaksCleaner()
    text = "Intelli-\n gence is cool."
    out = c.apply(text)
    # Hyphenation across newline removed
    assert "Intelli- gence" not in out
    assert "Intelligence" in out


def test_pdf_linebreaks_cleaner_merge_single_newlines():
    c = PDFLineBreaksCleaner()
    text = "This is a line\nthat should merge."
    out = c.apply(text)
    # Single newline in the middle of a sentence becomes a space
    assert "\nthat" not in out
    assert "line that" in out


def test_pdf_linebreaks_cleaner_collapse_blank_lines():
    c = PDFLineBreaksCleaner()
    text = "A\n\n\n\nB"
    out = c.apply(text)
    # 3+ line breaks collapse to exactly two
    assert out == "A\n\nB"


def test_chain_idempotency():
    chain = CleanerChain.from_names(["ftfy", "clean_text", "pdf_breaks"])
    sample = "URL http://example.com\nNew-\n line"
    once = chain.apply(sample)
    twice = chain.apply(once)
    assert once == twice


def test_unknown_cleaner_raises():
    with pytest.raises(ValueError):
        CleanerChain.from_names(["does_not_exist"])


@pytest.mark.parametrize(
    "names",
    [
        ["ftfy"],
        ["clean_text"],
        ["pdf_breaks"],
        ["ftfy", "clean_text"],
        ["ftfy", "clean_text", "pdf_breaks"],
    ],
)
def test_combinations_do_not_crash(names):
    chain = CleanerChain.from_names(names)
    out = chain.apply("Sample-\n text with http://example.com and  multiple   spaces")
    assert isinstance(out, str)
