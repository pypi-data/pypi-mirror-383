from __future__ import annotations

from .base import ICleaner

try:
    # `clean-text` package
    from cleantext import clean as clean_text_impl
except Exception:
    clean_text_impl = None


class CleanTextCleaner(ICleaner):
    """Remove common noise using `clean-text` while preserving useful tokens.

    Defaults are aligned with the project’s pipeline:
      - Keep case (lower=False)
      - Remove URLs/emails/phone numbers
      - Keep numbers and punctuation (can be changed in code if needed)
      - Preserve line breaks (can be changed in code if needed)
    """

    def __init__(
        self,
        *,
        lower: bool = False,
        no_urls: bool = True,
        no_emails: bool = True,
        no_phone_numbers: bool = True,
        no_numbers: bool = False,
        no_punct: bool = False,
        no_line_breaks: bool = False,
        replace_with_url: str = " ",
        replace_with_email: str = " ",
        replace_with_number: str = " ",
    ) -> None:
        self.kw = dict(
            lower=lower,
            no_urls=no_urls,
            no_emails=no_emails,
            no_phone_numbers=no_phone_numbers,
            no_numbers=no_numbers,
            no_punct=no_punct,
            no_line_breaks=no_line_breaks,
            replace_with_url=replace_with_url,
            replace_with_email=replace_with_email,
            replace_with_number=replace_with_number,
        )

    def apply(self, text: str) -> str:
        if not text or clean_text_impl is None:
            return text
        out = clean_text_impl(text, **self.kw)
        # Collapse extraneous whitespace introduced by replacements
        return " ".join(out.split())
