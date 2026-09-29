"""Teste de integração de verdade: conecta no servidor MCP do mytek-hub
(local ou o que estiver configurado em MYTEK_HUB_MCP_URL) e confere que o
agente consegue completar um pedido de ponta a ponta — LLM decide chamar
uma tool, a tool roda contra o servidor MCP de verdade, o resultado volta
pro LLM, e ele responde.

Só roda se houver credenciais configuradas (GROQ_API_KEY,
MYTEK_HUB_MCP_URL, MYTEK_HUB_MCP_TOKEN) — sem elas, os testes são pulados
em vez de falhar, pra não quebrar em CI/máquinas sem o mytek-hub rodando.
"""

import os

import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()

pytestmark = pytest.mark.skipif(
    not all(
        os.environ.get(var)
        for var in ("GROQ_API_KEY", "MYTEK_HUB_MCP_URL", "MYTEK_HUB_MCP_TOKEN")
    ),
    reason="precisa de GROQ_API_KEY, MYTEK_HUB_MCP_URL e MYTEK_HUB_MCP_TOKEN configurados",
)


async def test_agent_calls_a_real_tool_and_answers():
    from agent import build_agent

    agent = await build_agent()
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content="Quais projetos eu tenho?")]}
    )

    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) >= 1, "o agente deveria ter chamado pelo menos uma tool"

    resposta_final = result["messages"][-1]
    assert resposta_final.content, "deveria ter dado uma resposta final em texto"
