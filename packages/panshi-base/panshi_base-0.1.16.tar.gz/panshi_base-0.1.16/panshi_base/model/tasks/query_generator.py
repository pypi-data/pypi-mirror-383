from typing import List

from pydantic import BaseModel

from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_query_generator_path = NLP_TRADITION_PATH + NlpTask.QUERY_GENERATOR.value
llm_query_generator_path = NLP_LLM_PATH + NlpTask.QUERY_GENERATOR.value

"""
eg: 
    request: 
            {
                "texts": ["2022年，中国房地产进入转型阵痛期，传统“高杠杆、快周转”的模式难以为继，万科甚至直接喊话，中国房地产进入“黑铁时代”"],
                "limit":2
            }

    answer: {
                "code": 200,
                "msg" : "成功",
                "data":[
                   [
                        "中国房地产界的“黑铁时代”到几年结束？",
                        "中国房地产业曾被称为什么时代的最强房地产商？",
                   ]
                ]
            }       
"""


# 请求参数
class QueryGeneratorRequest(BaseModel):
    """
        texts: 文本信息集合.
        limit : 生成数量
    """
    texts: List[str]
    limit: int = 5


# 请求结果
class QueryGeneratorResponse(CommonResponse):
    """
        texts与data一一对应
    """
    data: List[List[str]]
