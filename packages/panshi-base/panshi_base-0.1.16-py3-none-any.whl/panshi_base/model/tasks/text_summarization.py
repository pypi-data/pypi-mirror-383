from typing import List

from pydantic import BaseModel

from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_text_summarization_path = NLP_TRADITION_PATH + NlpTask.TEXT_SUMMARIZATION.value
llm_text_summarization_path = NLP_LLM_PATH + NlpTask.TEXT_SUMMARIZATION.value

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
                    "万科喊话：中国房地产进入“黑铁时代”"
                ]
            }       
"""


# 请求参数
class TextSummarizationRequest(BaseModel):
    """
        texts: 文本信息集合.
    """
    texts: List[str]


# 请求结果
class TextSummarizationResponse(CommonResponse):
    """
        texts与data一一对应
    """
    data: List[str]
