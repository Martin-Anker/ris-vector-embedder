from openai import OpenAI
import os

client = OpenAI(
    api_key="XXX",
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
