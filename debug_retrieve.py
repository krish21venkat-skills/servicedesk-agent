# debug_retrieve.py
from rag_pipeline import collection

results = collection.query(query_texts=["What is the maternity leave policy?"], n_results=5)

for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
    print(f"distance={dist:.3f}  policy_type={meta['policy_type']}")
    print(doc[:150])
    print("---")