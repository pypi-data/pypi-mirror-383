from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from pydantic import Field, BaseModel

try:
    from pymilvus import FieldSchema, DataType
except ImportError:
    raise ValueError("pymilvus is not installed. Please install it with `pip install pymilvus`")

DEFAULT_PK_FIELD = "id"
DEFAULT_TEXT_FIELD = "text"
DEFAULT_VECTOR_FIELD = "vector"
DEFAULT_SCORE_FIELD = "score"


class BaseEntity(BaseModel, ABC):
    score: float = 0.0

    @abstractmethod
    def get_text(self) -> str:
        pass


class BasicEntity(BaseEntity):
    id: str = Field(description="ID信息")
    text: str = Field(description="标题信息")
    score: float = 0.0

    def get_text(self) -> str:
        return self.text


class CollectionInfo(ABC):
    collection_name: str
    fields: List[FieldSchema] = Field(description="字段集合")
    index_params: dict
    search_params: dict
    pk_field: str
    text_field: str
    vector_field: str

    def __init__(self, collection_name, fields, index_params, search_params, pk_field, text_field, vector_field):
        self.collection_name = collection_name
        self.fields = fields
        self.index_params = index_params
        self.search_params = search_params
        self.pk_field = pk_field
        self.text_field = text_field
        self.vector_field = vector_field

    @abstractmethod
    def to_entity(self, data: Dict[str, Any]) -> BaseEntity:
        pass


class BasicCollectionInfo(CollectionInfo, ABC):

    def __init__(self, dim: int, collection_name: str):
        fields = [
            FieldSchema(name=DEFAULT_PK_FIELD, dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name=DEFAULT_TEXT_FIELD, dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name=DEFAULT_VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=dim)
        ]
        fields.extend(self.get_custom_fields())
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        super().__init__(collection_name, fields, index_params, search_params, DEFAULT_PK_FIELD, DEFAULT_TEXT_FIELD,
                         DEFAULT_VECTOR_FIELD)

    @staticmethod
    def get_custom_fields() -> List[FieldSchema]:
        """
        添加额外的字段
        :param fields:
        :return:
        """
        return []


class VectorSearchParams(BaseModel):
    query: str
    expr: Optional[str] = None
    top_k: int = 10
