from openai import OpenAI
import os

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

text = "Diskriminierung aufgrund des Geschlechts ist verboten."

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=text
)

embedding = response.data[0].embedding

print("Embedding dimension:", len(embedding))
print("Embedding vector:")
print(embedding)
