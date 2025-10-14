from typing import List

try:
    from langchain_core.embeddings import Embeddings

except ImportError:
    raise ValueError("langchain is not installed. Please install it with `poetry add langchain`")

try:
    from panshi2task.client import PanshiTaskClient
except ImportError:
    raise ValueError("langchain is not installed. Please install it with `poetry add langchain`")


class PanShiEmbedding(Embeddings):

    def __init__(self, panshi_client: PanshiTaskClient):
        self.panshi_client: PanshiTaskClient = panshi_client

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        return self.panshi_client.batch_embedding(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.panshi_client.embedding(text)
