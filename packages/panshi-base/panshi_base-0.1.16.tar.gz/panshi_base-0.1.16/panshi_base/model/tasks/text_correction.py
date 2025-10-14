from typing import List

from pydantic import BaseModel
from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_text_correction_path = NLP_TRADITION_PATH + NlpTask.TEXT_CORRECTION.value
llm_text_correction_path = NLP_LLM_PATH + NlpTask.TEXT_CORRECTION.value

"""
eg: 
    request: 
            {
                "data": ["遇到逆竟时，我们必须勇于面对，而且要愈挫愈勇。","失败是成工之母"]
            }
    
    answer: {
                "code": 200,
                "msg" : "成功",
                "data":[
                    {
                        "source": "遇到逆竟时，我们必须勇于面对，而且要愈挫愈勇。",
                        "target": "遇到逆境时，我们必须勇于面对，而且要愈挫愈勇。",
                        "errors": [
                            {
                                "start_pos": 3,
                                "end_pos": 3,
                                "error": "竟",
                                "correct": "境"
                            }
                        ]
                    },
                    {
                        "source": "失败是呈贡之母",
                        "target": "失败是成功之母",
                        "errors": [
                            {
                                "start_pos": 3,
                                "end_pos": 4,
                                "error": "呈贡",
                                "correct": "成功"
                            }
                        ]
                    }
                ]
            }       
"""


# 请求参数
class TextCorrectionRequest(BaseModel):
    """
        texts: 文本信息集合.
    """
    texts: List[str]


class ErrorItem(BaseModel):
    start_pos: int
    end_pos: int
    error: str
    correct: str


class CorrectionItem(BaseModel):
    source: str
    target: str
    errors: List[ErrorItem]


# 请求结果
class TextCorrectionResponse(CommonResponse):
    """
        texts与data一一对应
    """
    data: List[CorrectionItem]
