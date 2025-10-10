from _typeshed import Incomplete
from enum import Enum
from pydantic import BaseModel, computed_field
from typing import Literal
from virt_llm import AsyncLLMClient as AsyncLLMClient
from virtualitics_sdk.elements.element import ElementType as ElementType

logger: Incomplete

class RawChatContext(BaseModel):
    user_id: str
    app_id: str
    chat_id: str
    chat_index: int
    step_name: str
    element_id: str
    prompt: str
    llm_host: str
    model: str
    response: str | None
    llm_client: AsyncLLMClient | None
    class Config:
        arbitrary_types_allowed: bool

class ProcessedChatMessage(BaseModel):
    role: Literal['user', 'system']
    content: str

class ChatSource(BaseModel):
    title: str
    element_type: str

class ChatSourceCard(BaseModel):
    title: str
    data: list[ChatSource]
    def to_dict(self): ...

class AvailableEvents(Enum):
    MESSAGE: str
    CHAT_END: str
    PAGE_UPDATE: str
    PAGE_REFRESH: str
    UPDATE_THINKING: str
    POST_PROCESSING: str
    EXCEPTION: str

class StreamMessage(BaseModel):
    """Event for a single message token in the stream."""
    t: Literal[AvailableEvents.MESSAGE]
    d: str

class StreamSourceInformation(BaseModel):
    """Event for the final, post-processed response."""
    t: Literal[AvailableEvents.POST_PROCESSING]
    d: list[ChatSourceCard]

class StreamPageRefresh(BaseModel):
    """Event to signal a trigger to refresh the current page"""
    t: Literal[AvailableEvents.PAGE_REFRESH]
    d: Literal['']

class StreamChatEnd(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal[AvailableEvents.CHAT_END]
    d: Literal['']

class DashboardFilter(BaseModel):
    element_id: str
    selected: str | list | dict | None
    @computed_field
    @property
    def element_type(self) -> str: ...

class ActionPageUpdate(BaseModel):
    card_id: str
    step_name: str
    filters: list[DashboardFilter] | None

class StreamActionPageUpdate(BaseModel):
    """Trigger the frontend to perform a Page Update"""
    t: Literal[AvailableEvents.PAGE_UPDATE]
    d: ActionPageUpdate

class StreamThinking(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal[AvailableEvents.UPDATE_THINKING]
    d: str

class StreamExecutingTool(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal['tool']
    d: str

class StreamWaitingForInput(BaseModel):
    """Event to signal the end of the chat stream."""
    t: Literal['waiting']
    d: Literal['']

class StreamException(BaseModel):
    t: Literal[AvailableEvents.EXCEPTION]
    d: str
StreamEvent = StreamMessage | StreamSourceInformation | StreamChatEnd | StreamActionPageUpdate | StreamThinking | StreamExecutingTool | StreamWaitingForInput | StreamException
