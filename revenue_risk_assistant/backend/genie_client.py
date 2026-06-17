from datetime import timedelta
from typing import Optional

from revenue_risk_assistant.backend.databricks_auth import get_workspace_client
from revenue_risk_assistant.backend.serialization import to_dict
from revenue_risk_assistant.settings import GENIE_SPACE_ID


def ask_genie(question: str, conversation_id: Optional[str]) -> tuple[dict, Optional[str]]:
    if not GENIE_SPACE_ID:
        raise ValueError("GENIE_SPACE_ID is not set. Add a Genie Space resource or set it in .env.")

    workspace = get_workspace_client()
    if conversation_id:
        message = workspace.genie.create_message_and_wait(
            space_id=GENIE_SPACE_ID,
            conversation_id=conversation_id,
            content=question,
            timeout=timedelta(minutes=5),
        )
    else:
        message = workspace.genie.start_conversation_and_wait(
            space_id=GENIE_SPACE_ID,
            content=question,
            timeout=timedelta(minutes=5),
        )

    message_dict = to_dict(message)
    return message_dict, message_dict.get("conversation_id") or conversation_id


def extract_text_and_sql(message_dict: dict) -> tuple[Optional[str], Optional[str]]:
    attachments = message_dict.get("attachments") or []
    response_text = None
    generated_sql = None

    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue

        text_obj = attachment.get("text")
        if isinstance(text_obj, dict):
            response_text = text_obj.get("content") or text_obj.get("value") or response_text
        elif isinstance(text_obj, str):
            response_text = text_obj

        query_obj = attachment.get("query")
        if isinstance(query_obj, dict):
            generated_sql = (
                query_obj.get("query")
                or query_obj.get("sql")
                or query_obj.get("statement")
                or generated_sql
            )
        elif isinstance(query_obj, str):
            generated_sql = query_obj

    return response_text, generated_sql
