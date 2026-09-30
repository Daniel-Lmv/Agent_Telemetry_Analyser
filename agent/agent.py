from agent.schemas import TelemetryAnalysis
from agentkit import LLMAPI, Agent


def create_agent(llm: LLMAPI, tools: list) -> Agent:
    """
    Cria o agente responsável pela análise de telemetria.
    """

    return Agent(
        llm=llm,
        tools=tools,
        max_steps=30,
    )


def generate_analysis(
    llm: LLMAPI,
    messages: list[dict],
) -> TelemetryAnalysis:
    """
    Converte o histórico final da execução do agente
    em uma análise estruturada.
    """

    return llm.generate_structured(
        messages,
        TelemetryAnalysis,
    )
