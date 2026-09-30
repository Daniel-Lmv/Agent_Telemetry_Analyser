from agent.prompt import SYSTEM_PROMPT
from agent.schemas import TelemetryAnalysis
from agentkit import LLMAPI, Agent


def create_agent(
    llm: LLMAPI,
    tools: list,
    max_steps: int = 10,
) -> Agent:
    return Agent(
        llm=llm,
        tools=tools,
        max_steps=max_steps,
    )


def run_analysis(
    agent: Agent,
    user_input: str,
) -> list[dict]:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    return agent.run(messages)


def generate_analysis(
    llm: LLMAPI,
    messages: list[dict],
) -> TelemetryAnalysis:

    return llm.generate_structured(
        messages,
        TelemetryAnalysis,
    )
