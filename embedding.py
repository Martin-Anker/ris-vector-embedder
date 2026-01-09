from sentence_transformers import SentenceTransformer

from article_db import load_all_absatze, load_all_embeddings, save_embedding

# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_article_absatz_embedding(article_metadata: dict, absatz: tuple[str, str]):

    """Embed the article metadata and its paragraphs into vectors."""
    # Combine article metadata into a single string
    metadata_parts = [
        f"Kurztitel: {article_metadata.get('Kurztitel', '')}",
        f"Typ: {article_metadata.get('Typ', '')}",
        f"§/Artikel/Anlage: {article_metadata.get('Paragraph_Artikel_Anlage', '')}",
        f"Schlagworte: {article_metadata.get('Schlagworte', '')}",
    ]
    metadata_text = "\n".join(metadata_parts)

    # Prepare texts for embedding: metadata and paragraph
    absatz_number, absatz_text = absatz
    embedding_text = metadata_text + f"\nAbsatz {absatz_number}: {absatz_text}"

    # Generate embeddings
    embeddings = model.encode(embedding_text)
    return embeddings

def cosine_similarity(a, b):
    dot_product = sum([x * y for x, y in zip(a, b)])
    norm_a = sum([x ** 2 for x in a]) ** 0.5
    norm_b = sum([x ** 2 for x in b]) ** 0.5
    return dot_product / (norm_a * norm_b)

def retrive(query, top_n=3):
    embeddings = load_all_embeddings()

    query_embedding = model.encode(query)

    similarities = []
    for absatz_id, embedding_vector in embeddings:
        similarity = cosine_similarity(query_embedding, embedding_vector)
        similarities.append((absatz_id, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_n]

def embed_all_absatze():
    print("Loading all absatze from the database...")
    absatze = load_all_absatze()

    for absatz_id, absatz_text in absatze:
        print(f"Embedding Absatz ID: {absatz_id}")
        embedding_vector = model.encode(absatz_text)
        save_embedding(absatz_id, embedding_vector)