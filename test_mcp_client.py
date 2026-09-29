"""Testes de mcp_client.py — só a parte pura (montagem da config de
conexão), sem rede. A conexão de verdade com o servidor MCP é coberta
pelo teste de integração em test_agent_live.py (roda só se houver um
mytek-hub local disponível)."""

import mcp_client


def test_server_config_reads_from_env(monkeypatch):
    monkeypatch.setenv("MYTEK_HUB_MCP_URL", "http://localhost:3000/api/mcp")
    monkeypatch.setenv("MYTEK_HUB_MCP_TOKEN", "now_teste123")

    config = mcp_client._server_config()

    assert config["now_organiza"]["transport"] == "streamable_http"
    assert config["now_organiza"]["url"] == "http://localhost:3000/api/mcp"
    assert config["now_organiza"]["headers"]["Authorization"] == "Bearer now_teste123"


def test_server_config_raises_without_required_env(monkeypatch):
    monkeypatch.delenv("MYTEK_HUB_MCP_URL", raising=False)
    monkeypatch.delenv("MYTEK_HUB_MCP_TOKEN", raising=False)

    try:
        mcp_client._server_config()
        assert False, "deveria ter levantado KeyError sem as env vars"
    except KeyError:
        pass
