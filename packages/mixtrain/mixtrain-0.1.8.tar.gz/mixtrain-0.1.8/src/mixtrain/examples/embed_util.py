import os

from cachew import cachew
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyBv1mHQq_GPiEFJx25cy8bgAqhuFkqKNSA"))

# TODO: Handle batching
# TODO: Handle multiple models
# TODO: Handle multiple tasks
# TODO: Handle multiple dimensions
# TODO: Handle multiple contents
# TODO: Handle normalization
@cachew(maxsize=1000)
def embed_text(text: str):
    result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(task_type="CLUSTERING", output_dimensionality=3072)).embeddings
    return result.embeddings[0].values

