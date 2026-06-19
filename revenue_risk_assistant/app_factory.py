from pathlib import Path

from dash import Dash

from revenue_risk_assistant.frontend.callbacks import register_callbacks
from revenue_risk_assistant.frontend.layout import build_layout

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_FOLDER = PROJECT_ROOT / "assets"

FONT_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com">'
FONT_LINK += '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
FONT_LINK += (
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
)


def create_app() -> Dash:
    app = Dash(
        __name__,
        title="Wanderbricks Revenue Assistant",
        suppress_callback_exceptions=True,
        assets_folder=str(ASSETS_FOLDER),
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    app.index_string = app.index_string.replace("</head>", f"{FONT_LINK}</head>")
    app.layout = build_layout()
    register_callbacks(app)
    return app
