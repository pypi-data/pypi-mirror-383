from enum import Enum
from typing import List

from pydantic import BaseModel

from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_text_embedding_path = NLP_TRADITION_PATH + NlpTask.TEXT_EMBEDDING.value
llm_text_embedding_path = NLP_LLM_PATH + NlpTask.TEXT_EMBEDDING.value

"""
eg: 
    request: 
            {
                "texts": ["2022年，中国房地产进入转型阵痛期，传统“高杠杆、快周转”的模式难以为继，万科甚至直接喊话，中国房地产进入“黑铁时代”"]
            }

    answer: {
                "code": 200,
                "msg" : "成功",
                "data":[
                    [1.0,...]
                ]
            }       
"""


class EmbeddingModels(Enum):
    """
    支持的向量模型枚举
    """
    TEXT2VEC = "text2vec-base-chinese"
    M3E = "m3e-base"


# 请求参数
class TextEmbeddingRequest(BaseModel):
    """
        texts: 文本信息集合.
        model_name : 模型名称
    """
    texts: List[str]
    model_name: str = EmbeddingModels.M3E.value


# 请求结果
class TextEmbeddingResponse(CommonResponse):
    """
        文本分类结果.texts与categories一一对应
    """
    data: List[List[float]]
