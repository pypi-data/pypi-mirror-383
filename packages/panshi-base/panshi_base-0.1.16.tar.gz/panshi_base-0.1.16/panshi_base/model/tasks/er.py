from typing import List, Dict, Optional

from pydantic import BaseModel

from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_er_path = NLP_TRADITION_PATH + NlpTask.RE.value
llm_er_path = NLP_LLM_PATH + NlpTask.RE.value

"""
eg: 
    request: 
            {
                "schema": {"竞赛名称": ["主办方", "承办方", "已举办次数"]},
                "texts": ["2022语言与智能技术竞赛由中国中文信息学会和中国计算机学会联合主办，百度公司、中国中文信息学会评测工作委员会和中国计算机学会自然语言处理专委会承办，已连续举办4届，成为全球最热门的中文NLP赛事之一。"]
            }

    answer: {
                "code": 200,
                "msg" : "成功",
                "data": [
                    {
                        "竞赛名称": [
                            {
                                "text": "2022语言与智能技术竞赛",
                                "start": 0,
                                "end": 13,
                                "probability": 0.7826019499807586,
                                "relations": {
                                    "主办方": [
                                        {
                                            "text": "中国中文信息学会",
                                            "start": 14,
                                            "end": 22,
                                            "probability": 0.8421450431136215
                                        },
                                        {
                                            "text": "中国计算机学会",
                                            "start": 23,
                                            "end": 30,
                                            "probability": 0.7578627511341374
                                        }
                                    ],
                                    "承办方": [
                                        {
                                            "text": "百度公司",
                                            "start": 35,
                                            "end": 39,
                                            "probability": 0.8291364956587657
                                        },
                                        {
                                            "text": "中国计算机学会自然语言处理专委会",
                                            "start": 56,
                                            "end": 72,
                                            "probability": 0.6188996457754641
                                        },
                                        {
                                            "text": "中国中文信息学会评测工作委员会",
                                            "start": 40,
                                            "end": 55,
                                            "probability": 0.6995462878816241
                                        }
                                    ],
                                    "已举办次数": [
                                        {
                                            "text": "4届",
                                            "start": 80,
                                            "end": 82,
                                            "probability": 0.46642794468009896
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }       
"""


# 请求参数
class ERequest(BaseModel):
    schema: List[str]
    texts: List[str]


class RelationItem(BaseModel):
    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    probability: Optional[float] = None


class ERItem(BaseModel):
    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    probability: Optional[float] = None
    relations: Dict[str:List[RelationItem]]


# 请求结果
class ERResponse(CommonResponse):
    data: List[Dict[str, List[ERItem]]]
