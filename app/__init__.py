"""Application package."""

from app.constants import APP_NAME, APP_VERSION
from app.state import AppState

# Import application lazily to avoid circular imports
def get_application():
    from app.application import CrosshairOverlayApplication, main
    return CrosshairOverlayApplication, main

__all__ = [
    "APP_NAME",
    "APP_VERSION",
    "AppState",
    "get_application",
]