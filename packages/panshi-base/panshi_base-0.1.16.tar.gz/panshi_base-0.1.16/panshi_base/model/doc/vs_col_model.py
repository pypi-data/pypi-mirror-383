from typing import Any, Dict

from panshi_base.model.doc.vs_model import BaseEntity, TitleEntity, ParagraphEntity, SummaryEntity
from panshi_base.model.milvus_model import CollectionInfo, VECTOR_FIELD

try:
    from pymilvus import FieldSchema, DataType
except ImportError:
    raise ValueError(
        "pymilvus is not installed. Please install it with `pip install pymilvus`"
    )
FILE_ID_FIELD = "file_id"
TITLE_ID_FIELD = "title_id"
SOURCE_TYPE_FIELD = "source_type"


class TitleCollectionInfo(CollectionInfo):
    def __init__(self, dim: int, collection_name: str):
        text_field = "title"
        fields = [
            FieldSchema(name=TITLE_ID_FIELD, dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name=text_field, dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name=FILE_ID_FIELD, dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name=SOURCE_TYPE_FIELD, dtype=DataType.VARCHAR, max_length=36)
        ]
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        super().__init__(collection_name, fields, index_params, search_params, TITLE_ID_FIELD, text_field)

    def to_entity(self, data: Dict[str, Any]) -> BaseEntity:
        return TitleEntity.model_validate(data)


class ParagraphCollectionInfo(CollectionInfo):

    def __init__(self, dim: int, collection_name: str):
        paragraph_id_field = "paragraph_id"
        text_field = "paragraph"
        fields = [
            FieldSchema(name=paragraph_id_field, dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name=text_field, dtype=DataType.VARCHAR, max_length=8000),
            FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name=TITLE_ID_FIELD, dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name=FILE_ID_FIELD, dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name=SOURCE_TYPE_FIELD, dtype=DataType.VARCHAR, max_length=36)
        ]
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        super().__init__(collection_name, fields, index_params, search_params, paragraph_id_field, text_field)

    def to_entity(self, data: Dict[str, Any]) -> BaseEntity:
        return ParagraphEntity.model_validate(data)


class SummaryCollectionInfo(CollectionInfo):
    def __init__(self, dim: int, collection_name: str):
        text_field = "summary"
        fields = [
            FieldSchema(name=FILE_ID_FIELD, dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name=text_field, dtype=DataType.VARCHAR, max_length=3000),
            FieldSchema(name=VECTOR_FIELD, dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        super().__init__(collection_name, fields, index_params, search_params, FILE_ID_FIELD, text_field)

    def to_entity(self, data: Dict[str, Any]) -> BaseEntity:
        return SummaryEntity.model_validate(data)
