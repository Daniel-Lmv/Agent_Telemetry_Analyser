# Agent Telemetry Analyser

Projeto da Avaliação da Unidade I de IA Agêntica.

O notebook principal está em:

`notebook/Agent_Telemetry_Analyser.ipynb`

Versão do notebook para rodar no Google Colab:

`notebook/Agent_Telemetry_Analyser_Colab.ipynb`

## Entregável

O entregável da atividade é o notebook. A primeira célula de código do notebook procura os arquivos do projeto no ambiente atual. Caso eles não estejam presentes, ela clona este repositório com `git clone`, instala as dependências Python de `requirements.txt` no ambiente ativo e adiciona a raiz do projeto ao `sys.path`.

Na versão do notebook usando Google Colab, ignore o passo a passo a seguir, basta rodar as células. 

Essa célula não instala Ollama, não baixa modelos do Ollama e não configura GPU. Essas etapas dependem do computador do usuário e devem ser feitas previamente por quem for executar o notebook.

## Como executar

1. Instale e inicie o Ollama por conta própria.
2. Escolha e baixe um modelo com suporte a tool/function calling.

Modelo usado nos testes deste projeto:

```powershell
ollama pull qwen3.5:4b
```

O modelo não precisa ser obrigatoriamente o mesmo, mas precisa chamar ferramentas de forma consistente. Durante os testes, modelos muito pequenos, incluindo modelos de aproximadamente 2B e 0.8B parâmetros, não funcionaram bem: eles não geraram as chamadas de ferramenta ou as saídas esperadas.

3. Opcionalmente, crie e ative um ambiente Python:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Instale as dependências Python:

```powershell
pip install -r requirements.txt
```

5. Execute o notebook do início ao fim.

Se o notebook for executado sozinho, fora da pasta do projeto, ele tentará clonar este repositório automaticamente. Se o repositório já estiver clonado, mantenha a estrutura de pastas original para que os módulos locais `agent`, `agentkit`, `core` e `tools` sejam encontrados.

## Dependências Python

As dependências mínimas estão em `requirements.txt`:

- `pandas`, para carregar e processar a telemetria.
- `numpy`, usado por componentes auxiliares do `agentkit`.
- `pydantic`, para validar a saída estruturada dos testes.
- `ipykernel`, para facilitar a execução em ambiente de notebook.

O projeto usa `LLMAPI` apontando para o Ollama local, portanto não exige `torch` nem `transformers` para a execução principal do notebook. Essas bibliotecas só seriam necessárias se alguém optasse por trocar o notebook para usar um modelo local carregado diretamente em Python.
