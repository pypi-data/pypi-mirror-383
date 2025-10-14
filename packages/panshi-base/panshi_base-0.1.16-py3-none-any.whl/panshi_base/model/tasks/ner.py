from typing import List, Optional, Dict

from pydantic import BaseModel
from panshi_base.model.response import CommonResponse
from panshi_base.model.tasks.base import NLP_LLM_PATH, NLP_TRADITION_PATH, NlpTask

# 路径信息
tradition_ner_path = NLP_TRADITION_PATH + NlpTask.NER.value
llm_ner_path = NLP_LLM_PATH + NlpTask.NER.value

"""
eg: 
    request: 
            {
                "schema": ["时间", "选手", "赛事名称"],
                "texts": ["2月8日上午北京冬奥会自由式滑雪女子大跳台决赛中中国选手谷爱凌以188.25分获得金牌！"]
            }

    answer: {
                "code": 200,
                "msg" : "成功",
                "data": [
                    {
                        "时间": [
                            {
                                "text": "2月8日上午",
                                "start": 0,
                                "end": 6,
                                "probability": 0.9857575576790722
                            }
                        ],
                        "选手": [
                            {
                                "text": "谷爱凌",
                                "start": 28,
                                "end": 31,
                                "probability": 0.898201529424199
                            }
                        ],
                        "赛事名称": [
                            {
                                "text": "北京冬奥会自由式滑雪女子大跳台决赛",
                                "start": 6,
                                "end": 23,
                                "probability": 0.8500797764697232
                            }
                        ]
                    }
                ]
            }       
"""


class NerItem(BaseModel):
    text: str
    start: Optional[int] = None
    end: Optional[int] = None
    probability: Optional[float] = None


# 请求参数
class NERRequest(BaseModel):
    schema: List[str]
    texts: List[str]


# 请求结果
class NERResponse(CommonResponse):
    data: List[Dict[str, List[NerItem]]]
