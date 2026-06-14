"""
Agent client — bridges Streamlit UI and the ADK Supervisor agent.
Yields (author, text) tuples so the UI can render reasoning steps incrementally.
"""

import asyncio
import uuid
from typing import AsyncGenerator

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agents.supervisor import supervisor


async def stream_agent(
    user_message: str,
    project_id: str,
) -> AsyncGenerator[tuple[str, str], None]:
    """
    Run the supervisor and yield (author, text) for each reasoning step.
    The last yielded item with author == 'final' contains the complete report.
    """
    session_service = InMemorySessionService()
    session_id = str(uuid.uuid4())

    await session_service.create_session(
        app_name="ai-agent",
        user_id="user",
        session_id=session_id,
    )

    runner = Runner(
        agent=supervisor,
        session_service=session_service,
        app_name="ai-agent",
    )

    full_prompt = f"{user_message}\n\nProject ID: {project_id}"
    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=full_prompt)],
    )

    final_text = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        new_message=message,
    ):
        if not event.content or not event.content.parts:
            continue

        author = getattr(event, "author", "agent")
        for part in event.content.parts:
            text = getattr(part, "text", "") or ""
            if not text:
                continue

            if event.is_final_response():
                final_text += text
            else:
                yield (author, text)

    if final_text:
        yield ("final", final_text)


def run_agent(user_message: str, project_id: str):
    """Synchronous wrapper — collects all events and returns (trace_steps, final_report)."""
    trace, report = [], ""

    async def _collect():
        nonlocal report
        async for author, text in stream_agent(user_message, project_id):
            if author == "final":
                report = text
            else:
                trace.append((author, text))

    asyncio.run(_collect())
    return trace, report
