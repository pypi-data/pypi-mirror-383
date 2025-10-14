from abc import ABC
from typing import Callable

try:
    from langchain_community.vectorstores import Milvus
except ImportError:
    raise ValueError("langchain is not installed. Please install it with `poetry add langchain`")


class PanShiMilvus(Milvus, ABC):
    @staticmethod
    def _cosine_relevance_score_fn(score: float) -> float:
        """Normalize the score on a scale [0, 1]."""
        return score

    @staticmethod
    def _l2_relevance_score_fn(score: float) -> float:
        return (score + 1) / 2

    def _select_relevance_score_fn(self) -> Callable[[float], float]:
        if self.search_params["metric_type"] == 'COSINE':
            return self._cosine_relevance_score_fn
        elif self.search_params["metric_type"] == 'L2':
            return self._l2_relevance_score_fn
        else:
            raise ValueError(
                "Unknown distance strategy, must be cosine, max_inner_product "
                "(dot product), or euclidean"
            )
