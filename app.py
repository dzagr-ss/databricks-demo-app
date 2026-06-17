from revenue_risk_assistant.app_factory import create_app
from revenue_risk_assistant.settings import runtime_port

app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=runtime_port(), debug=False)
