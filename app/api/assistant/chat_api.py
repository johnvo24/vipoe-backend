from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.assistant import ChatMessageRequest
from app.services.geminiai_service import GEMINI_INSTANCE
from app.rag.rag_web import build_prompt_with_context, build_prompt_without_context, search_all_queries
from app.services.web_context_service import summarize_contexts_by_chunks

router = APIRouter()

@router.post("/chat", status_code=status.HTTP_200_OK)
async def create_item(
  req: ChatMessageRequest,
  current_user: User = Depends(get_current_user)
):
  if req.model == GEMINI_INSTANCE.name:
    try:
      if not req.prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
      if len(req.prompt) > 256:
        raise HTTPException(status_code=400, detail="Prompt exceeds maximum length of 256 characters")
      if req.search_mode:
        contexts_dict = await search_all_queries(
          queries=[req.prompt],
          api_key=settings.GOOGLE_API_KEY,
          cx=settings.SEARCH_ENGINE_ID,
        )
        if not contexts_dict["contexts"]:
          raise HTTPException(status_code=404, detail="No relevant information found for the given prompt")
        
        summaries_data = await summarize_contexts_by_chunks(
          contexts_dict=contexts_dict,
          prompt=req.prompt,
          gemini=GEMINI_INSTANCE
        )

        last_prompt = build_prompt_with_context(
          prompt=req.prompt,
          summaries_data=summaries_data
        )
      else:
        last_prompt = build_prompt_without_context(req.prompt)

      print(last_prompt)
      answer = GEMINI_INSTANCE.__generate__(last_prompt)
      return {"prompt": req.prompt,"answer": answer}
    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
  else:
    raise HTTPException(status_code=400, detail="Model not supported")