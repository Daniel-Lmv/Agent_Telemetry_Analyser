from agentkit import LLMAPI

MODEL = "qwen3:4b"

llm = LLMAPI(
    model=MODEL,
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    temperature=0.0,
    max_tokens=1024,
)

response = llm.invoke("Responda em apenas uma frase: o que é telemetria?")

print("TIPO:", type(response))
print("RESPOSTA:", repr(response))
print("LEN:", len(response))
