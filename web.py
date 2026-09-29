"""Interface web (chat) pro agente — pra visualizar e usar sem precisar
de terminal. Mostra em tempo real quando o agente decide chamar uma
ferramenta do mytek-hub (e o resultado dela), não só a resposta final —
é isso que torna visível que é um agente agindo, não um chat comum.
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel

from agent import build_agent

load_dotenv()

INDEX_HTML_PATH = Path(__file__).parent / "static" / "index.html"

_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    _state["agent"] = await build_agent()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


@app.get("/")
def index():
    return FileResponse(INDEX_HTML_PATH, media_type="text/html")


@app.get("/health")
def health():
    return {"status": "ok"}


def _history_to_messages(history: list[ChatMessage]):
    out = []
    for m in history:
        out.append(HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content))
    return out


@app.post("/chat")
async def chat(req: ChatRequest):
    agent = _state["agent"]
    messages = _history_to_messages(req.history) + [HumanMessage(content=req.message)]

    def sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    async def event_stream():
        try:
            async for step in agent.astream({"messages": messages}, stream_mode="values"):
                last = step["messages"][-1]

                if isinstance(last, AIMessage) and last.tool_calls:
                    for tc in last.tool_calls:
                        yield sse({"type": "tool_call", "name": tc["name"], "args": tc["args"]})

                elif isinstance(last, ToolMessage):
                    content = last.content
                    if isinstance(content, list):
                        content = " ".join(
                            c.get("text", "") for c in content if isinstance(c, dict)
                        )
                    yield sse({"type": "tool_result", "text": content})

                elif isinstance(last, AIMessage) and last.content and not last.tool_calls:
                    yield sse({"type": "content", "text": last.content})

            yield sse({"type": "done"})
        except Exception as exc:
            yield sse({"type": "error", "text": str(exc)})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
