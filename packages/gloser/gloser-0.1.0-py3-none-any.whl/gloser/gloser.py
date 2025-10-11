"""Main Gloser implementation"""

from typing import Dict, Optional, Any


class Gloser:
    """Simple internationalization manager for Python applications."""

    def __init__(self, default_locale: str = "en"):
        """
        Initialize Gloser with a default locale.

        Args:
            default_locale: The default locale to use (default: "en")
        """
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, str]] = {}

    def add_translations(self, locale: str, translations: Dict[str, str]) -> None:
        """
        Add translations for a specific locale.

        Args:
            locale: The locale code (e.g., "en", "es", "fr")
            translations: Dictionary mapping keys to translated strings
        """
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale].update(translations)

    def set_locale(self, locale: str) -> None:
        """
        Set the current locale.

        Args:
            locale: The locale code to set as current
        """
        self.current_locale = locale

    def translate(self, key: str, locale: Optional[str] = None, **kwargs: Any) -> str:
        """
        Translate a key to the current or specified locale.

        Args:
            key: The translation key
            locale: Optional locale to use (defaults to current_locale)
            **kwargs: Format arguments for the translation string

        Returns:
            The translated string, or the key if translation not found
        """
        target_locale = locale or self.current_locale

        if target_locale in self.translations and key in self.translations[target_locale]:
            translation = self.translations[target_locale][key]
            if kwargs:
                return translation.format(**kwargs)
            return translation

        # Fallback to default locale
        if target_locale != self.default_locale:
            if self.default_locale in self.translations and key in self.translations[self.default_locale]:
                translation = self.translations[self.default_locale][key]
                if kwargs:
                    return translation.format(**kwargs)
                return translation

        # Return the key if no translation found
        return key


# Global instance for convenience
_default_gloser = Gloser()


def translate(key: str, locale: Optional[str] = None, **kwargs: Any) -> str:
    """
    Convenience function to translate using the default Gloser instance.

    Args:
        key: The translation key
        locale: Optional locale to use
        **kwargs: Format arguments for the translation string

    Returns:
        The translated string
    """
    return _default_gloser.translate(key, locale, **kwargs)
