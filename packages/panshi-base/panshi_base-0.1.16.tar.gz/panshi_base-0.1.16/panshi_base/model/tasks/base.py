from enum import Enum

# 传统小模型实现的任务服务的基础路径
NLP_TRADITION_PATH = "/nlp/tradition"
# 大语言模型实现的任务服务的基础路径
NLP_LLM_PATH = "/nlp/llm"


class NlpTask(Enum):
    # 文本分类
    TEXT_CLASSIFICATION = "text_classification"
    # 文本向量化
    TEXT_EMBEDDING = "text_embedding"
    # 问题生成
    QUERY_GENERATOR = "query_generator"
    # 标签挖掘
    TAG_EXCAVATE = "tag_excavate"
    # 问答对挖掘
    QA_EXCAVATE = "qa_excavate"
    # 文本纠错
    TEXT_CORRECTION = "text_correction"
    # 文本摘要
    TEXT_SUMMARIZATION = "text_summarization"
    # 命名实体识别
    NER = "ner"
    # 关系抽取
    RE = "re"
