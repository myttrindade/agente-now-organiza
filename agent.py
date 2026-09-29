"""Agente autônomo (LangGraph) que opera o Now Organiza (mytek-hub) por
conta própria, a partir de um pedido em linguagem natural.

Diferente do RAG do mytek-chat (que só recupera contexto pra responder),
esse agente decide sozinho *quais ações tomar* — pode encadear várias
chamadas de tool numa única conversa (ex.: "organiza a reunião de hoje:
cria uma tarefa de follow-up pro João e outra pra Maria" exige descobrir
quem é "João"/"Maria" e chamar `now_criar_tarefa` duas vezes, sem que
ninguém precise dizer isso passo a passo).

O agente em si é o padrão ReAct do LangGraph (`langchain.agents.create_agent`): o
modelo decide chamar uma tool ou responder, o resultado da tool volta pro
modelo, e repete até ele decidir que a resposta está completa. As tools
não são hardcoded aqui — vêm do servidor MCP do mytek-hub em tempo real
(ver mcp_client.py), então o agente sempre reflete as tools que existem
*agora* no mytek-hub, mesmo que ele ganhe novas no futuro.
"""

from langchain.agents import create_agent
from langchain_groq import ChatGroq

from mcp_client import get_mytek_hub_tools

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = (
    "Você é um assistente que opera o Now Organiza (sistema de tarefas da "
    "mytek) em nome da pessoa que está conversando com você, usando as "
    "ferramentas disponíveis (now_listar_projetos, now_criar_tarefa, "
    "now_listar_tarefas, now_atualizar_status_tarefa, now_editar_tarefa, "
    "now_comentar_tarefa).\n\n"
    "Regras:\n"
    "- Antes de criar/editar algo num projeto específico, confirme o nome "
    "exato do projeto com now_listar_projetos se não tiver certeza — não "
    "adivinhe.\n"
    "- Se o pedido envolver várias ações (ex.: criar tarefas pra várias "
    "pessoas), execute uma de cada vez e confira o resultado de cada "
    "chamada antes de seguir pra próxima.\n"
    "- Se uma ferramenta retornar erro (ex.: nome ambíguo, tarefa não "
    "encontrada), não desista nem invente — leia a mensagem de erro (ela "
    "já explica o que fazer) e tente de novo com a correção.\n"
    "- Depois de agir, responda pra pessoa em português, de forma direta, "
    "confirmando o que foi feito (com link, quando a ferramenta devolver "
    "um).\n"
    "- Nunca invente que uma ação foi feita sem ter chamado a ferramenta "
    "correspondente de verdade."
)


async def build_agent():
    tools = await get_mytek_hub_tools()
    model = ChatGroq(model=MODEL, temperature=0.2)
    return create_agent(model, tools, system_prompt=SYSTEM_PROMPT)
