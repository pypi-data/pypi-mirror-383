from typing import Dict, List, Any

try:
    from elasticsearch import Elasticsearch, helpers
except ImportError:
    raise ValueError("elasticsearch is not installed. Please install it with `poetry add elasticsearch`")

from loguru import logger
from pydantic import BaseModel


class ElasticSearchConf(BaseModel):
    host: str
    port: int
    index: str


class ElasticSearchService:
    client: Elasticsearch = None
    index: str = None

    def __init__(self, params: Dict):
        """
        加载配置信息
        :return:
        """
        conf = ElasticSearchConf.model_validate(params)
        self.conf = conf
        self.index = conf.index
        self.__create_client__()

    def __create_client__(self):
        """
        创建客户端连接
        :return:
        """
        self.client = Elasticsearch([{"host": self.conf.host, "port": self.conf.port}])
        logger.info("初始化es客户端")

    def query_scroll(self, query: Dict, scroll: str = '1m') -> List[Dict[str, Any]]:
        documents: List[Dict[str, Any]] = []
        for hit in helpers.scan(self.client, index=self.index, body=query, scroll=scroll):
            documents.append(hit['_source'])
        return documents
