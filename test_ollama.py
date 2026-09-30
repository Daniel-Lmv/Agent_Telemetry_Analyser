from agent.agent import create_agent, generate_analysis
from agentkit import LLMAPI
from core.preprocessing import preprocess_telemetry
from core.telemetry import Telemetry
from tools.comparison_tools import create_comparison_tools
from tools.lap_tools import create_lap_tools
from tools.section_tools import create_section_tools

# --------------------------------------------------
# Telemetria
# --------------------------------------------------

telemetry = Telemetry.from_file("data/sessao.csv")

laps, track_length = preprocess_telemetry(telemetry.data)


# --------------------------------------------------
# Ferramentas
# --------------------------------------------------

lap_tools = create_lap_tools(laps)
comparison_tools = create_comparison_tools(laps)
section_tools = create_section_tools(laps)

tools = lap_tools + comparison_tools + section_tools


# --------------------------------------------------
# Modelo
# --------------------------------------------------

MODEL = "qwen3.5:4b"

llm = LLMAPI(
    model=MODEL,
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    temperature=0.0,
    max_tokens=4096,
)


# --------------------------------------------------
# Agente
# --------------------------------------------------

agent = create_agent(llm, tools)

# --------------------------------------------------
# Teste
# --------------------------------------------------

history = agent.run(
    "Por que a volta 7 perdeu tempo no setor 2 em relação à volta 5? "
    "Analise esse setor usando a telemetria disponível."
)

result = generate_analysis(llm, history)

print(result)
