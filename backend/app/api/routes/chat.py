from fastapi import APIRouter

from backend.app.api.dependencies import ContainerDependency
from backend.app.api.schemas.chat import ChatRequest, ChatResponse
from backend.app.domain.entities.chat import ChatMessage

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, container: ContainerDependency) -> ChatResponse:
    messages = tuple(ChatMessage(message.role, message.content) for message in request.messages)
    result = await container.answer_question.execute(messages)
    return ChatResponse.from_domain(result)

