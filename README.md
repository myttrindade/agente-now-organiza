# agente-now-organiza

Agente autônomo (LangGraph) que opera o **Now Organiza** — o sistema de
tarefas do [mytek-hub](https://github.com/myttrindade/mytek-hub) — a
partir de um pedido em linguagem natural, decidindo sozinho quais
ferramentas chamar e em qual ordem.

Diferente de um RAG (que só recupera contexto pra responder), esse é um
agente que **age**: cria tarefa, edita, muda status, comenta — de
verdade, no sistema real — encadeando quantas chamadas forem necessárias
até resolver o pedido.

## Como funciona

```
pedido em linguagem natural
        │
        ▼
   ┌─────────┐   decide chamar uma tool    ┌──────────────────┐
   │   LLM   │ ───────────────────────────▶│  servidor MCP do  │
   │ (Groq)  │◀─────────────────────────── │     mytek-hub      │
   └─────────┘   resultado da tool          └──────────────────┘
        │
        ▼ (repete até achar que a tarefa está completa)
   resposta final
```

- **`mcp_client.py`** — conecta no servidor MCP do mytek-hub
  (`/api/mcp`, autenticado por token pessoal) via
  [`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters)
  e busca as tools disponíveis **em tempo real** — o agente nunca tem uma
  lista de tools hardcoded; se o mytek-hub ganhar uma tool nova amanhã, o
  agente já enxerga ela sem precisar de deploy aqui.
- **`agent.py`** — monta o agente (`langchain.agents.create_agent`,
  padrão ReAct do LangGraph) com essas tools e um modelo da Groq.
- **`cli.py`** — interface de linha de comando pra conversar com o
  agente, mantendo o histórico da conversa entre pedidos.

## Exemplo real (rodado contra um mytek-hub local)

```
você> Cria uma tarefa "Revisar proposta do cliente Ampla" pra mim, com
prazo 2026-10-05, e depois me confirma listando minhas tarefas de hoje
em diante.

  [chama now_criar_tarefa] → "Tarefa criada em 'Geral' (status: A fazer). /board"
  [chama now_listar_tarefas] → "- [A fazer] Revisar proposta do cliente Ampla (Geral) — prazo 2026-10-05"

agente> Tarefa criada com sucesso:

Revisar proposta do cliente Ampla – responsável: você, prazo:
2026-10-05, status: A fazer, projeto: Geral.

Suas tarefas atuais (responsável = você) são:
- Revisar proposta do cliente Ampla – A fazer – Geral
```

O agente decidiu sozinho encadear as duas chamadas (criar → confirmar
listando) a partir de um único pedido em português — não foi dito passo a
passo o que chamar.

## Rodando

1. Tenha o [mytek-hub](https://github.com/myttrindade/mytek-hub) rodando
   (local ou publicado) e gere um token pessoal em `/conta/ia`.
2. ```bash
   cp .env.example .env   # preencha GROQ_API_KEY, MYTEK_HUB_MCP_URL, MYTEK_HUB_MCP_TOKEN
   pip install -r requirements.txt
   python cli.py
   ```

## Testes

```bash
pip install -r requirements-dev.txt
pytest -v
```

- `test_mcp_client.py`: testes unitários, sem rede.
- `test_agent_live.py`: teste de integração de verdade — conecta no
  servidor MCP real e confere que o agente completa um pedido de ponta a
  ponta. Pulado automaticamente se `GROQ_API_KEY`/`MYTEK_HUB_MCP_URL`/
  `MYTEK_HUB_MCP_TOKEN` não estiverem configurados (ex.: numa máquina sem
  o mytek-hub rodando).
