"""CLI pra conversar com o agente — cada pedido pode disparar uma ou
várias chamadas de tool no Now Organiza antes de responder."""

import asyncio

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent import build_agent

load_dotenv()


async def main():
    print("Conectando no servidor MCP do mytek-hub...")
    agent = await build_agent()
    print("Pronto. Peça algo (ex.: 'quais tarefas eu tenho hoje?'). Ctrl+C pra sair.\n")

    history: list = []
    while True:
        try:
            pedido = input("você> ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not pedido:
            continue

        history.append(HumanMessage(content=pedido))
        resultado = await agent.ainvoke({"messages": history})
        history = resultado["messages"]

        resposta = history[-1]
        print(f"\nagente> {resposta.content}\n")


if __name__ == "__main__":
    asyncio.run(main())
