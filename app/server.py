"""HTTP API for the support assistant.

A business embeds web/widget.html on its site. Each customer message arrives
here, the language model writes the reply, and the whole exchange is stored.
"""

import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from app import model, transcripts

app = FastAPI(title="Support assistant")

# Businesses embed the widget on their own domains.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST"])

# Each business's staff read their own conversations with a key of their own:
# STAFF_KEYS="key-for-store-a:store-a,key-for-store-b:store-b"
STAFF_KEYS = dict(
    pair.split(":", 1)
    for pair in os.environ.get("STAFF_KEYS", "").split(",")
    if ":" in pair and pair.split(":", 1)[0]
)


def staff_business(x_staff_key: str = Header(default="")) -> str:
    """The business whose staff key this is; anything else is refused."""
    for key, business_id in STAFF_KEYS.items():
        if hmac.compare_digest(key, x_staff_key):
            return business_id
    raise HTTPException(status_code=401, detail="unknown staff key")


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
    if msg.conversation_id and transcripts.business_of(msg.conversation_id) != msg.business_id:
        raise HTTPException(status_code=404, detail="no such conversation")
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


@app.get("/conversations")
def conversations(business_id: str = Depends(staff_business)) -> list[dict]:
    """Every stored conversation for the caller's own business, for its staff to review."""
    return transcripts.for_business(business_id)
