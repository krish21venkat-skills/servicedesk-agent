import chromadb
from chromadb.utils import embedding_functions
import ollama, os
from pathlib import Path

embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("kb_collection", embedding_function=embedder)

# Distance threshold — chunks farther than this from the query are treated as
# "not relevant enough" rather than blindly included. Tune this after testing
# (Step 3 below) — lower means stricter matching, higher means more lenient.
RELEVANCE_THRESHOLD = 0.7  # tuned against real Chroma L2 distances — see debug_retrieve.py output

def index_documents(folder=r"D:\Python\servicedesk_agent\knowledge_base", reset=True):
    """Index every policy doc in the folder. Each file's own name becomes its
    'policy_type' tag, so retrieval results can be attributed to leave policy,
    VPN policy, password policy, etc. — whatever files you drop in."""
    if reset:
        # Clears old entries first so re-running this doesn't fail on duplicate
        # IDs when you add/update policy documents later.
        existing = collection.get()
        if existing["ids"]:
            collection.delete(ids=existing["ids"])

    for f in Path(folder).glob("**/*.*"):
        if f.suffix not in (".md", ".txt"):
            continue
        text = f.read_text(errors="ignore")
        chunks = [text[i:i+800] for i in range(0, len(text), 700)]
        policy_type = f.stem.replace("_", " ").replace("-", " ")  # e.g. "leave_policy" -> "leave policy"
        collection.add(
            documents=chunks,
            ids=[f"{f.stem}-{j}" for j in range(len(chunks))],
            metadatas=[{"source": str(f), "policy_type": policy_type} for _ in chunks]
        )
    print(f"Indexed {collection.count()} chunks from {folder}")

def retrieve(query, k=5):
    """Retrieve top-k chunks across ALL indexed policy documents, then drop any
    result whose distance shows it's not actually relevant to the query — this
    stops irrelevant policies from being handed to the LLM just because k=5
    always returns something."""
    results = collection.query(query_texts=[query], n_results=k)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    relevant = [
        (doc, meta) for doc, meta, dist in zip(docs, metas, distances)
        if dist <= RELEVANCE_THRESHOLD
    ]
    return relevant

def answer_with_context(query):
    chunks = retrieve(query)

    if not chunks:
        return (
            "I couldn't find anything in the company policy documents that "
            "answers this. Could you rephrase, or specify which policy area "
            "you're asking about (leave, VPN, password reset, etc.)?",
            []
        )

    # Group context by policy_type so the LLM (and the user) can see which
    # document(s) the answer is actually drawing from.
    context_blocks = []
    sources_used = set()
    for doc, meta in chunks:
        context_blocks.append(f"[{meta['policy_type']}]\n{doc}")
        sources_used.add(meta["policy_type"])
    context = "\n---\n".join(context_blocks)

    resp = ollama.chat(
        model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a company policy assistant. You have access to multiple "
                    "policy documents (leave, IT/VPN, password reset, and others). "
                    "Answer the user's question using ONLY the context provided below, "
                    "which is tagged by policy area in [brackets]. If the question spans "
                    "more than one policy area, address each relevant part using its "
                    "matching context. Keep the answer concise and directly relevant.\n\n"
                    "If the context does not contain enough information to answer the "
                    "question, say so plainly and do not make anything up.\n\n"
                    f"Context:\n{context}"
                )
            },
            {"role": "user", "content": query}
        ]
    )

    answer = resp["message"]["content"]
    sources_note = f"\n\n(Sources: {', '.join(sorted(sources_used))})"
    print("from rag ==== ", answer)
    return answer + sources_note, chunks

