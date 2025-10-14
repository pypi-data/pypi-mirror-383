from typing import List

from pydantic import BaseModel

from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_text_classification_path = NLP_TRADITION_PATH + NlpTask.TEXT_CLASSIFICATION.value
llm_text_classification_path = NLP_LLM_PATH + NlpTask.TEXT_CLASSIFICATION.value

"""
eg: 
    request: 
            {
                "texts": ["2022年，中国房地产进入转型阵痛期，传统“高杠杆、快周转”的模式难以为继，万科甚至直接喊话，中国房地产进入“黑铁时代”"],
                "categories": ["人物","国家组织","政策法规"]
            }

    answer: {
                "code": 200,
                "msg" : "成功",
                "data":[
                    ["政策法规"]
                ]
            }       
"""


# 请求参数
class TextClassificationRequest(BaseModel):
    """
        texts: 待分类的文本信息集合.
        categories : 分类体系集合
    """
    texts: List[str]
    categories: List[str]


# 请求结果

class TextClassificationResponse(CommonResponse):
    """
        文本分类结果.texts与categories一一对应
    """
    data: List[List[str]]
