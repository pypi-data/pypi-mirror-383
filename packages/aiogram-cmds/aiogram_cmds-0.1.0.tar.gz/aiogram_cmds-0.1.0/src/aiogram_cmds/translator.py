"""
Translator protocol and adapters for i18n integration.
"""

from typing import Protocol


class Translator(Protocol):
    """Protocol for translation functions."""

    def __call__(self, key: str, *, locale: str) -> str | None: ...


def build_translator_from_i18n(i18n_obj) -> Translator:
    """
    Build translator adapter from an aiogram i18n instance exposing gettext(key, locale=?).
    """

    def _t(key: str, *, locale: str) -> str | None:
        try:
            value = i18n_obj.gettext(key, locale=locale)
            if not value or value == key:
                return None
            return value
        except Exception:
            return None

    return _t


def noop_translator(key: str, *, locale: str) -> str | None:
    """No-op translator that always returns None."""
    return None
