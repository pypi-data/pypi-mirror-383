import json
from typing import List

try:
    import requests
except ImportError:
    raise ValueError("requests is not installed. Please install it with `poetry add requests`")

try:
    from langchain.schema.embeddings import Embeddings
except ImportError:
    raise ValueError("langchain is not installed. Please install it with `poetry add langchain`")
from loguru import logger


class PanshiInferenceAPIEmbeddings(Embeddings):
    """Embed texts using the Panshi API.
    """
    server_url: str
    model_name: str = "m3e-base"
    """The name of the model to use for text embeddings."""

    def __init__(self, url, em_model_name, dim: int):
        self.server_url = url
        self.model_name = em_model_name
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }
        response = requests.post(
            self.server_url,
            headers=headers,
            data=json.dumps({
                "sentences": texts,
                "model_name": self.model_name
            }),
        )
        # 接收返回的文件流
        if response.status_code == 200:
            result = response.json()
            if result["code"] == 200:
                return result["data"]
            else:
                logger.error(f"请求失败：{result['msg']}")
        else:
            logger.error("请求失败，状态码：", response.status_code)
        raise RuntimeError("embedding失败,服务异常")

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a Panshi API.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        return self.embed_documents([text])[0]
