"""
RAG pipeline configuration (chunk size, overlap, top_k, etc.).
Populated fully in Step 4 (Chunker) and Step 6 (Retrieval).
Kept as a stub now so the folder structure is already in place.
"""
CHUNK_SIZE = 800          # characters per chunk (tuned later)
CHUNK_OVERLAP = 100       # characters of overlap between chunks
TOP_K_RESULTS = 5         # number of chunks retrieved per query
