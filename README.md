# LexLint sample: a customer-support chatbot

A small sample app for trying [LexLint](https://lexlint.io). It is not a product,
nobody runs it, and it is not maintained beyond keeping it a fair example.

The app is a support assistant that a software company sells to other
businesses. A business puts the chat widget on its own website; the widget sends
each customer message to the server, the server asks a large language model to
write the reply, and the conversation is stored so the business can review it.

## Try LexLint on it

Connect LexLint to your assistant (in Claude, add it as a connector with the
URL `https://mcp.lexlint.io/mcp`), then ask:

> Use LexLint to lint the app at github.com/ungovr/lexlint-sample-chatbot. It
> serves customers in California and the European Union. We built the AI
> system, we process customer data for the businesses that buy it, and no
> public body runs or buys it.

Your assistant reads the code, confirms what the app does and where it
operates, and LexLint returns findings tied to the laws that apply, each with
its citation.

## What is in it

| Path | What it does |
|---|---|
| `app/server.py` | The HTTP API: takes a customer's message, asks the model for a reply, returns it; a business's staff read its own conversations with their staff key |
| `app/model.py` | The call to the language model that writes each reply |
| `app/transcripts.py` | Stores every conversation, with the customer's name and email address |
| `web/widget.html` | The chat widget a business embeds on its website |

## Run it (optional)

You do not need to run it for a lint. If you want to:

```bash
pip install -r requirements.txt
export MODEL_API_URL=https://your-model-provider.example/v1/generate
export MODEL_API_KEY=...
export STAFF_KEYS="a-long-random-key:demo-store"
uvicorn app.server:app --reload
```

## License

MIT. See [LICENSE](LICENSE).
