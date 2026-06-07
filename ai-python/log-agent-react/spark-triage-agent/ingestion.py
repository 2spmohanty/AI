from vector_ops import parse_log, collection


def ingest_log_file(file_path: str):
    """Parses and seeds files directly into ChromaDB vector spaces."""
    candidates = parse_log(file_path)
    if not candidates:
        print(f"Skipping {file_path}: No error footprints detected.")
        return

    collection.upsert(
        ids=[c["id"] for c in candidates],
        documents=[c["document"] for c in candidates],
        metadatas=[c["metadata"] for c in candidates]
    )
    print(f"Successfully ingested {len(candidates)} anomaly segments from {file_path}.")


training_data_path = "/Users/smruti/Dev/2spmohanty/AI/scrimba-ai-python/log-agent-react/log_samples/training_data"
import os
for filename in os.listdir(training_data_path):
    log_file_path = os.path.join(training_data_path, filename)
    print(f"Ingesting {log_file_path}...")
    ingest_log_file(log_file_path)
print("Data inserted to VEctor DB.")