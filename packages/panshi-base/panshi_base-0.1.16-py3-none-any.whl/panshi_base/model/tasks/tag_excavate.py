from typing import List, Optional

from pydantic import BaseModel
from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_tag_excavate_path = NLP_TRADITION_PATH + NlpTask.TAG_EXCAVATE.value
llm_tag_excavate_path = NLP_LLM_PATH + NlpTask.TAG_EXCAVATE.value

"""
eg: 
    request: 
            {
                "texts": ["2022年，中国房地产进入转型阵痛期，传统“高杠杆、快周转”的模式难以为继，万科甚至直接喊话，中国房地产进入“黑铁时代”"],
                "themes": []
            }

    answer: {
                "code": 200,
                "msg" : "成功",
                "data":[
                    ["黑铁时代","万科"]
                ]
            }       
"""


# 请求参数
class TagExcavateRequest(BaseModel):
    """
        texts: 文本信息集合.
        themes : 主题信息.
            设置后:将在设置的主题内,挖掘标签信息
            没设置:将进行开放式挖掘
    """
    texts: List[str]
    themes: Optional[List[str]] = []


# 请求结果
class TagExcavateResponse(CommonResponse):
    """
        texts与data一一对应
    """
    data: List[List[str]]
