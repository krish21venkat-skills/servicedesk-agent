from rag_pipeline import retrieve
from main import should_escalate
from llm_router import classify_email

intent = classify_email("Leave Policy", "What is the maternity leave policy?")
chunks = retrieve("What is the maternity leave policy?")
print("Chunks found:", len(chunks))
print("Policy types:", {meta["policy_type"] for _, meta in chunks})
print(should_escalate(intent, chunks))