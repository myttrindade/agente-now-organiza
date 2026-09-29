"""Conexão com o servidor MCP do mytek-hub (Now Organiza).

O mytek-hub expõe um servidor MCP (Model Context Protocol) em
`/api/mcp`, com tools pra operar o sistema de tarefas (criar, listar,
editar, comentar) — autenticado por token pessoal
(`app/api/[transport]/route.ts` no repositório do mytek-hub).

Este módulo é o lado *cliente* desse mesmo protocolo: busca as tools
disponíveis no servidor (via `langchain-mcp-adapters`) e devolve elas já
no formato que o LangGraph consegue usar direto, sem precisar descrever
manualmente o schema de cada tool aqui.
"""

import os

from langchain_mcp_adapters.client import MultiServerMCPClient


def _server_config() -> dict:
    url = os.environ["MYTEK_HUB_MCP_URL"]
    token = os.environ["MYTEK_HUB_MCP_TOKEN"]
    return {
        "now_organiza": {
            "transport": "streamable_http",
            "url": url,
            "headers": {"Authorization": f"Bearer {token}"},
        }
    }


async def get_mytek_hub_tools() -> list:
    """Busca as tools do Now Organiza expostas no momento (lista dinâmica
    — se o mytek-hub adicionar/remover uma tool, o agente já vê, sem
    precisar mudar código aqui)."""
    client = MultiServerMCPClient(_server_config())
    return await client.get_tools()
