"""Bishnu Resume Python Package with Animations"""

from .resume import get_resume, DEFAULT_BIO, display_animated_resume, animate_runner, animate_loading

__all__ = ["get_resume", "DEFAULT_BIO", "display_animated_resume", "animate_runner", "animate_loading", "about"]

def about():
    return "This is Bishnu's Resume Python Package with Animations — created by Bishnu Sahu 🚀✨"
