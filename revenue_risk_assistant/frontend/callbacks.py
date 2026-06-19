import json

from dash import Input, Output, State, html, no_update

from revenue_risk_assistant.backend.dashboard_data import fetch_dashboard_data, fetch_years
from revenue_risk_assistant.backend.genie_client import ask_genie, extract_text_and_sql
from revenue_risk_assistant.backend.sql_client import run_sql
from revenue_risk_assistant.backend.sql_guard import readonly_sql
from revenue_risk_assistant.frontend.callback_helpers import build_metric_cards, render_chat_history
from revenue_risk_assistant.frontend.charts import auto_figure, monthly_revenue_figure, product_revenue_figure
from revenue_risk_assistant.frontend.components import empty_result, error_panel
from revenue_risk_assistant.frontend.grids import df_to_grid


def register_callbacks(app) -> None:
    app.callback(
        Output("year-filter", "options"),
        Output("year-filter", "value"),
        Input("refresh-button", "n_clicks"),
    )(load_years)

    app.callback(
        Output("kpi-cards", "children"),
        Output("monthly-revenue-chart", "figure"),
        Output("product-revenue-chart", "figure"),
        Output("risk-grid-container", "children"),
        Output("metrics-year-badge", "children"),
        Input("year-filter", "value"),
        Input("refresh-button", "n_clicks"),
    )(update_dashboard)

    app.callback(
        Output("chat-history", "data"),
        Output("chat-window", "children"),
        Output("sql-code", "children"),
        Output("genie-result-grid", "children"),
        Output("genie-result-chart", "figure"),
        Output("conversation-id", "data"),
        Output("raw-response", "children"),
        Output("genie-results-panel", "className"),
        Input("ask-button", "n_clicks"),
        State("preset-question", "value"),
        State("custom-question", "value"),
        State("conversation-id", "data"),
        State("chat-history", "data"),
        prevent_initial_call=True,
    )(submit_genie_question)

    app.callback(
        Output("custom-question", "value"),
        Input("preset-question", "value"),
    )(sync_preset_question)


def load_years(_n_clicks):
    try:
        years = fetch_years()
    except Exception:
        return [], None

    options = [{"label": str(year), "value": year} for year in years]
    return options, max(years) if years else None


def update_dashboard(selected_year, _n_clicks):
    if not selected_year:
        message = "Select a year after the SQL warehouse and demo views are available."
        return [error_panel("Dashboard data is not loaded", message)], {}, {}, html.Div(message), ""

    try:
        year = int(selected_year)
        data = fetch_dashboard_data(year)
    except Exception as exc:
        detail = str(exc)
        return [error_panel("Dashboard query failed", detail)], {}, {}, error_panel("Risk table unavailable", detail), ""

    cards = build_metric_cards(data["kpi"], data["support"], year)
    monthly_fig = monthly_revenue_figure(data["monthly"])
    product_fig = product_revenue_figure(data["product"])
    risk_grid = df_to_grid(data["risk"], page_size=12, height=410)

    return cards, monthly_fig, product_fig, risk_grid, f"Year {year}"


def sync_preset_question(preset_question):
    return preset_question or no_update


def submit_genie_question(_n_clicks, preset_question, custom_question, conversation_id, chat_history):
    question = (custom_question or preset_question or "").strip()
    if not question:
        return no_update, no_update, "", html.Div("Enter a question."), {}, conversation_id, "", no_update

    chat_history = chat_history or []
    chat_history.append({"role": "User", "content": question})

    try:
        message_dict, new_conversation_id = ask_genie(question, conversation_id)
        response_text, generated_sql = extract_text_and_sql(message_dict)
        answer = response_text or "Genie returned a response, but no text attachment was found. Check the raw response."
        chat_history.append({"role": "Genie", "content": answer})

        result_grid = empty_result("No SQL result to display.")
        result_fig = {}
        sql_text = generated_sql or "No generated SQL found in the Genie response."

        if generated_sql and readonly_sql(generated_sql):
            result_df = run_sql(generated_sql)
            result_grid = df_to_grid(result_df)
            result_fig = auto_figure(result_df)
        elif generated_sql:
            result_grid = empty_result("Generated SQL was not read-only. The app did not execute it.")

        return (
            chat_history,
            render_chat_history(chat_history),
            sql_text,
            result_grid,
            result_fig,
            new_conversation_id,
            json.dumps(message_dict, indent=2),
            "genie-results-panel",
        )
    except Exception as exc:
        chat_history.append({"role": "Error", "content": str(exc)})
        return (
            chat_history,
            render_chat_history(chat_history),
            "",
            error_panel("Genie call failed", str(exc)),
            {},
            conversation_id,
            str(exc),
            "genie-results-panel",
        )
