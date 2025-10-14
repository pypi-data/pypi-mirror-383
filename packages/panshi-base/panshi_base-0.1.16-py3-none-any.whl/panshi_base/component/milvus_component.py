from typing import List, Dict, Union, Any

from panshi_base.model.doc.vs_model import BaseEntity
from panshi_base.model.milvus_model import CollectionInfo, VectorSearchParams, DEFAULT_SCORE_FIELD

try:
    from langchain.schema.embeddings import Embeddings
except ImportError:
    raise ValueError("langchain is not installed. Please install it with `poetry add langchain`")

from loguru import logger

try:
    from pymilvus import CollectionSchema, connections, utility, Collection
except ImportError:
    raise ValueError("pymilvus is not installed. Please install it with `poetry add pymilvus`")


def conn_milvus(config: Dict):
    connections.connect(**config)
    logger.info("milvus连接成功...")


class MilvusComponent:
    def __init__(self, col_info: CollectionInfo, embedding_func: Embeddings, using: str = "default"):
        self.alias: str = using
        self.col_info = col_info
        self.embedding_func = embedding_func
        if not utility.has_collection(col_info.collection_name, using=self.alias):
            self._create_collection(col_info)
        # load
        self.col = self._load(col_info)

    def _create_collection(self, col_info: CollectionInfo):
        schema = CollectionSchema(
            fields=col_info.fields,
            enable_dynamic_field=False
        )
        col = Collection(
            name=col_info.collection_name,
            schema=schema,
            using=self.alias
        )
        col.create_index(
            field_name=col_info.vector_field,
            index_params=col_info.index_params
        )
        logger.info("Collection-[{}]创建完成", col_info.collection_name)

    def _load(self, col_info: CollectionInfo) -> Collection:
        collection = Collection(col_info.collection_name, using=self.alias)
        collection.load()
        logger.info("Collection-[{}]加载完成", col_info.collection_name)
        return collection

    def clean(self) -> bool:
        # 刪除所有数据
        expr = f"{self.col_info.pk_field} != \"-1111\""
        response = self.col.delete(expr)
        logger.info("[{}]===>成功删除{}条数据", self.col_info.collection_name, response.delete_count)
        return True

    def delete_by_pks(self, pks: List[str]) -> bool:
        expr = f"{self.col_info.pk_field} in {str(pks)}"
        response = self.col.delete(expr)
        logger.info("[{}]===>成功删除{}条数据", self.col_info.collection_name, response.delete_count)
        return True

    def count(self) -> int:
        return self.col.num_entities

    def batch_insert(self, entities: List[BaseEntity],
                     exclude_keys: Union[set[int], set[str], dict[int, Any], dict[str, Any], None] = None) -> bool:
        if exclude_keys is None:
            exclude_keys = []
        if DEFAULT_SCORE_FIELD not in exclude_keys:
            exclude_keys.append(DEFAULT_SCORE_FIELD)
        if len(entities) > 0:
            datas = [e.model_dump(exclude=exclude_keys) for e in entities]
            vectors = self.embedding_func.embed_documents([e.get_text() for e in entities])
            for i, d in enumerate(datas):
                d[self.col_info.vector_field] = vectors[i]
            response = self.col.insert(datas)
            logger.info("[{}]===>成功写入{}条数据", self.col_info.collection_name, response.succ_count)
        return True

    def similarity_search(self, search_params: VectorSearchParams, score_threshold: float) -> List[BaseEntity]:
        """
        :param search_params:
        :param score_threshold:
        :return:
        """
        vecs = self.embedding_func.embed_query(search_params.query)
        output_fields = self.get_output_fields()
        res = self.col.search(
            data=[vecs],
            anns_field=self.col_info.vector_field,
            param=self.col_info.search_params,
            limit=search_params.top_k,
            expr=search_params.expr,
            output_fields=output_fields,
        )
        ret = []
        for result in res[0]:
            meta = {x: result.entity.get(x) for x in output_fields}
            e = self.col_info.to_entity(meta)
            e.score = result.score
            if result.score > score_threshold:
                ret.append(e)
        return ret

    def get_output_fields(self):
        return [f.name for f in self.col_info.fields if f.name != self.col_info.vector_field]
