from pathlib import Path

from dash import Dash

from revenue_risk_assistant.frontend.callbacks import register_callbacks
from revenue_risk_assistant.frontend.layout import build_layout

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_FOLDER = PROJECT_ROOT / "assets"


def create_app() -> Dash:
    app = Dash(
        __name__,
        title="Revenue Risk Assistant",
        suppress_callback_exceptions=True,
        assets_folder=str(ASSETS_FOLDER),
    )
    app.layout = build_layout()
    register_callbacks(app)
    return app
