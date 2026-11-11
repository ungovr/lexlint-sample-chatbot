"""HTTP API for the support assistant.

A business embeds web/widget.html on its site. Each customer message arrives
here, the language model writes the reply, and the whole exchange is stored.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from app import model, transcripts

app = FastAPI(title="Support assistant")

# Businesses embed the widget on their own domains.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST"])


class ChatMessage(BaseModel):
    business_id: str
    conversation_id: str | None = None
    customer_name: str
    customer_email: EmailStr
    message: str


class ChatReply(BaseModel):
    conversation_id: str
    reply: str


@app.post("/chat", response_model=ChatReply)
def chat(msg: ChatMessage) -> ChatReply:
    conversation_id = msg.conversation_id or transcripts.new_conversation(
        business_id=msg.business_id,
        customer_name=msg.customer_name,
        customer_email=msg.customer_email,
    )
    history = transcripts.messages(conversation_id)
    transcripts.append(conversation_id, role="customer", text=msg.message)

    reply = model.write_reply(
        business_id=msg.business_id,
        customer_name=msg.customer_name,
        history=history,
        message=msg.message,
    )
    transcripts.append(conversation_id, role="assistant", text=reply)
    return ChatReply(conversation_id=conversation_id, reply=reply)


@app.get("/conversations/{business_id}")
def conversations(business_id: str) -> list[dict]:
    """Every stored conversation for one business, for its staff to review."""
    return transcripts.for_business(business_id)
