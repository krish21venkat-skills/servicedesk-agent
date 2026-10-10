Developed Sep-Oct 2026, uploaded to GitHub on 10 Oct 2026.

# ServiceDesk Agent

An AI-powered service desk agent that answers employee queries from a knowledge base (RAG), takes actions through tools (API, database, RPA, email, web portal) and escalates to a human when it cannot resolve a request.

Built as a hands-on practice project for GenAI / AI-agent development. It runs locally with open-source components, and all data in this repo is **dummy/sample data**.

---

## How it works

```
 Channels            Orchestration          Knowledge (RAG)         Tools / Actions
┌───────────┐      ┌───────────────┐      ┌─────────────────┐     ┌──────────────────┐
│ Slack     │      │ main.py       │      │ ChromaDB        │     │ API tool         │
│ Email     │ ───▶ │ LLM router    │ ───▶ │ Embeddings      │     │ DB tool          │
│ (inbox)   │      │ (intent →     │      │ knowledge_base/ │     │ RPA tool         │
└───────────┘      │  RAG / tool / │      └─────────────────┘     │ Email sender     │
                   │  escalation)  │                              │ Portal automation│
                   └───────┬───────┘                              └──────────────────┘
                           │
                  ┌────────▼────────┐
                  │ State & memory  │
                  │ tickets, chat   │
                  └─────────────────┘
```

## Project layers

| Layer | What it does | Files / folders |
|---|---|---|
| **1. Channels (input)** | Receives user requests from Slack and email | `slack_socket_listener.py`, `email_reader.py` |
| **2. Orchestration** | Entry point; the LLM router decides whether a request needs a knowledge answer, a tool action, or escalation | `main.py`, `llm_router.py` |
| **3. Knowledge (RAG)** | Chunks and embeds documents, retrieves the most relevant chunks, and answers only from that context | `rag_pipeline.py`, `knowledge_base/`, `chroma_db/` (generated) |
| **4. Tools (actions)** | Actions the agent can perform: call APIs, query the database, trigger RPA, send email, automate the web portal | `api_tool.py`, `db_tool.py`, `rpa_tool.py`, `email_sender.py`, `portal/` |
| **5. State & memory** | Stores tickets and conversation context | `ticket_store.py`, `memory_store.py` |
| **6. Escalation** | Hands off to a human when confidence is low or the request is out of scope | `escalation.py` |
| **7. Mocks & tests** | Fake API and portal for safe local testing; sanity tests | `mock_api.py`, `mock_portal.py`, `test_*.py`, `debug_retrieve.py` |

## Tools & technologies

| Area | Tool |
|---|---|
| Language | Python 3 |
| Local LLM | [Ollama](https://ollama.com) (`llama3.1:8b`) |
| Vector database | [ChromaDB](https://www.trychroma.com) (persistent) |
| Embeddings | `sentence-transformers` – `all-MiniLM-L6-v2` |
| Chat integration | Slack (Socket Mode) |
| Email | IMAP/SMTP via `email_reader` / `email_sender` |
| Web automation | Playwright |
| Config & secrets | `.env` file loaded with `python-dotenv` |

## Key behaviour

- **Answers only from the knowledge base.** If a query is unrelated to the documents (for example, a question about a favourite city in a leave-policy bot), the agent politely says it can only help with topics covered in the knowledge base.
- **Distance threshold** on retrieval results is used to detect off-topic queries before calling the LLM.
- **Tool use and escalation** are decided by the router, so simple questions stay fast and complex ones reach a human.

## Getting started

```powershell
# 1. Clone and enter the project
git clone https://github.com/<your-username>/servicedesk-agent.git
cd servicedesk-agent

# 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install

# 3. Pull the local model
ollama pull llama3.1:8b

# 4. Configure secrets (never commit the real .env)
copy .env.example .env
# open .env and fill in your own values

# 5. Index the knowledge base and run
python rag_pipeline.py
python main.py
```

## Configuration

Copy `.env.example` to `.env` and fill in your own values. The `.env` file is git-ignored and must never be committed. Typical settings include the Ollama model name, Slack tokens, and email/SMTP credentials; see `.env.example` for the exact variable names.

## Security notes

- No credentials, tokens or passwords are stored in this repository.
- `.env`, `chroma_db/` and local databases are excluded through `.gitignore`.
- All sample documents and tickets are dummy data; no real employee or customer data is included.

## Roadmap

- Better chunking (recursive splitter) and re-ranking
- Evaluation set for retrieval quality
- MCP-based tool interface
- Guardrails for prompt injection and unsafe output

## License

For learning and portfolio purposes.
