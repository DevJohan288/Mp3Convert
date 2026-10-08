"""Pruebas del validador de URLs. Correr con: pytest"""
from app.services import YouTubeURLValidator


def test_valid_watch_url():
    assert YouTubeURLValidator.is_valid("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


def test_valid_short_url():
    assert YouTubeURLValidator.is_valid("https://youtu.be/dQw4w9WgXcQ")


def test_valid_shorts_url():
    assert YouTubeURLValidator.is_valid("https://youtube.com/shorts/dQw4w9WgXcQ")


def test_valid_mobile_url():
    assert YouTubeURLValidator.is_valid("https://m.youtube.com/watch?v=dQw4w9WgXcQ")


def test_invalid_other_site():
    assert not YouTubeURLValidator.is_valid("https://vimeo.com/12345")


def test_invalid_empty_string():
    assert not YouTubeURLValidator.is_valid("")


def test_invalid_garbage_text():
    assert not YouTubeURLValidator.is_valid("esto no es un link")
