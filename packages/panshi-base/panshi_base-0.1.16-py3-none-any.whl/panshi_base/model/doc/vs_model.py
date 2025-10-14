import json
from typing import Optional

from pydantic import Field

from panshi_base.model.milvus_model import BaseEntity


class TitleEntity(BaseEntity):
    title_id: str = Field(description="标题ID信息")
    title: str = Field(description="标题信息")
    file_id: str = Field(description="所属文件ID")
    source_type: str = Field(description="文件来源")
    score: Optional[float] = 0.0

    def get_text(self) -> str:
        return self.title

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)


class ParagraphEntity(BaseEntity):
    paragraph_id: str = Field(description="段落ID信息")
    paragraph: str = Field(description="段落信息")
    title_id: str = Field(description="所属标题ID信息")
    file_id: str = Field(description="所属文件ID")
    source_type: str = Field(description="文件来源")
    score: Optional[float] = 0.0

    def get_text(self) -> str:
        return self.paragraph

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)


class SummaryEntity(BaseEntity):
    summary: str = Field(description="摘要")
    file_id: str = Field(description="文件ID")

    def get_text(self) -> str:
        return self.summary

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)
