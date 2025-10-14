import time
from typing import Optional, Literal, Dict, Union, List

from pydantic import BaseModel, Field

from panshi_base import get_exception_str


class ModelCard(BaseModel):
    id: str
    show_name: str
    order: int
    desc: str
    created: int = Field(default_factory=lambda: int(time.time()))


class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system", "function"]
    content: Optional[str]
    function_call: Optional[Dict] = None


class DeltaMessage(BaseModel):
    role: Optional[Literal["user", "assistant", "system"]] = None
    content: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    functions: Optional[List[Dict]] = None
    temperature: Optional[float] = 0.8
    top_p: Optional[float] = 0.8
    max_length: Optional[int] = 20 * 1000
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Literal["stop", "length", "function_call"]


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal["stop", "length"]]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal["chat.completion", "chat.completion.chunk"]
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))

    @staticmethod
    def stop(model: str, response_text: str):
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content=response_text),
            finish_reason="stop"
        )
        return ChatCompletionResponse(model=model, choices=[choice_data], object="chat.completion")

    @staticmethod
    def error(model: str, exc: Exception):
        error_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role="assistant", content=ErrorMessage(message=get_exception_str(exc)).str()),
            finish_reason="stop"
        )
        return ChatCompletionResponse(model=model, choices=[error_data], object="chat.completion")

    @staticmethod
    def stream_error(model: str, exc: Exception) -> str:
        error_choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(content=ErrorMessage(message=get_exception_str(exc)).stream_str()),
            finish_reason=None
        )
        chunk = ChatCompletionResponse(model=model, choices=[error_choice_data], object="chat.completion.chunk")
        return "{}".format(chunk.model_dump_json(exclude_unset=True, exclude_none=True))

    @staticmethod
    def stream_stop(model: str) -> str:
        choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(),
            finish_reason="stop"
        )
        chunk = ChatCompletionResponse(model=model, choices=[choice_data], object="chat.completion.chunk")
        return "{}".format(chunk.model_dump_json(exclude_unset=True, exclude_none=True))

    @staticmethod
    def stream_new(model: str, new_text: str) -> str:
        choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=DeltaMessage(content=new_text),
            finish_reason=None
        )
        chunk = ChatCompletionResponse(model=model, choices=[choice_data], object="chat.completion.chunk")
        return "{}".format(chunk.model_dump_json(exclude_unset=True, exclude_none=True))


class ErrorMessage(BaseModel):
    code: int = 500
    message: str

    def stream_str(self):
        json_str = "{}".format(self.model_dump_json(indent=4))
        return f'''```json\n{json_str}\n```'''

    def str(self):
        return "{}".format(self.model_dump_json(indent=4))
