from .base import NlpTask
from .er import tradition_er_path, llm_er_path, ERequest, ERResponse
from .ner import tradition_ner_path, llm_ner_path, NERRequest, NERResponse
from .qa_excavate import tradition_qa_excavate_path, llm_qa_excavate_path, QAExcavateRequest, QAExcavateResponse
from .query_generator import (
    tradition_query_generator_path,
    llm_query_generator_path,
    QueryGeneratorRequest,
    QueryGeneratorResponse
)
from .tag_excavate import tradition_tag_excavate_path, llm_tag_excavate_path, TagExcavateRequest, TagExcavateResponse
from .text_classification import (
    tradition_text_classification_path,
    llm_text_classification_path,
    TextClassificationRequest,
    TextClassificationResponse
)
from .text_correction import (
    tradition_text_correction_path,
    llm_text_correction_path,
    TextCorrectionRequest,
    TextCorrectionResponse
)
from .text_embedding import tradition_text_embedding_path, llm_text_embedding_path, TextEmbeddingRequest, \
    TextEmbeddingResponse

from .text_summarization import tradition_text_summarization_path, llm_text_summarization_path, \
    TextSummarizationRequest, TextSummarizationResponse
