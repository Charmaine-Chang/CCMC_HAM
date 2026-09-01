"""Internationalization and language management."""
from flask import session, request

LANGUAGES = {
    'zh': '中文',
    'en': 'English'
}


def get_locale():
    """Get current language. Priority: session > URL param > cookie > browser > default zh."""
    if 'language' in session:
        return session['language']

    language = request.args.get('lang')
    if language in LANGUAGES:
        session['language'] = language
        return language

    language = request.cookies.get('language')
    if language in LANGUAGES:
        return language

    best_match = request.accept_languages.best_match(LANGUAGES.keys())
    return best_match or 'zh'


def set_language(language):
    """Set the current language."""
    if language in LANGUAGES:
        session['language'] = language
        return True
    return False
