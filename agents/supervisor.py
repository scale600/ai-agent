"""
Supervisor Agent — entry point for all user requests.
Routes tasks to the appropriate sub-agent and streams reasoning back to the caller.
"""

import asyncio
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from agents.iam_audit_agent import iam_audit_agent
from config.settings import GEMINI_MODEL

supervisor = LlmAgent(
    name="supervisor",
    model=GEMINI_MODEL,
    description="Orchestrator that routes cloud operations requests to the right specialist agent.",
    instruction="""
You are an intelligent cloud operations assistant. Analyze the user's request and delegate to the right specialist:

- GCP IAM audit, permission review, service account analysis → transfer to iam_audit_agent

After the specialist completes its work, summarize the key findings for the user in plain language,
then present the full report it returned.
""",
    sub_agents=[iam_audit_agent],
)


async def run(user_message: str, session_id: str = "default") -> str:
    """
    Run the supervisor agent with a user message and return the final text response.
    Prints each event's reasoning step to stdout for tracing.
    """
    session_service = InMemorySessionService()
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

    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=user_message)],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        new_message=message,
    ):
        # Print reasoning trace
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    author = getattr(event, "author", "agent")
                    print(f"[{author}] {part.text[:200]}")

        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    final_response += part.text

    return final_response


if __name__ == "__main__":
    result = asyncio.run(
        run("Audit IAM policies for project your-project-id and generate a full report.")
    )
    print("\n===== FINAL REPORT =====")
    print(result)
