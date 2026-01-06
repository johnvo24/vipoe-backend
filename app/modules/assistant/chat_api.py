import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.assistant import ChatMessageRequest, EditStepRequest
from app.services.geminiai_service import GEMINI_INSTANCE
from app.rag.rag_web import build_edit_poem_prompt, build_prompt_with_context, build_prompt_without_context, search_all_queries
from app.services.web_context_service import summarize_contexts_by_chunks

router = APIRouter()

@router.post("/chat", status_code=status.HTTP_200_OK)
async def create_item(
  req: ChatMessageRequest,
  current_user: User = Depends(get_current_user)
):
  if req.model == GEMINI_INSTANCE.name or req.model == "auto":
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
  
@router.post("/edit", status_code=status.HTTP_200_OK)
async def edit_item(
  req: EditStepRequest,
  current_user: User = Depends(get_current_user)
):
  try:
    if not req.original_poem:
      raise HTTPException(status_code=400, detail="Original poem cannot be empty")
    if not hasattr(req, "original_poem") or not hasattr(req, "steps"):
      raise HTTPException(status_code=400, detail="Missing original_poem or steps in request")
    # Chỉ truyền các trường cần thiết trong từng step
    payload = {
      "original_poem": req.original_poem,
      "steps": [
        {
          "error_poem": step.error_poem,
          "step_content": step.step_content,
          "edited_poem": step.edited_poem
        } for step in req.steps
      ]
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
      response = await client.post("http://47.186.29.91:52887/edit-poem/step", json=payload)
      if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
      data = response.json()
    return data
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

# @router.post("/edit", status_code=status.HTTP_200_OK)
# async def edit_item(
#   req: ChatMessageRequest,
#   current_user: User = Depends(get_current_user)
# ):
#   if req.model == GEMINI_INSTANCE.name or req.model == "auto":
#     try:
#       if not req.prompt:
#         raise HTTPException(status_code=400, detail="Prompt cannot be empty")
#       if len(req.prompt) > 256:
#         raise HTTPException(status_code=400, detail="Prompt exceeds maximum length of 256 characters")
#       last_prompt = build_edit_poem_prompt(req.prompt)

#       print(last_prompt)
#       answer = GEMINI_INSTANCE.__generate__(last_prompt)
#       return {"prompt": req.prompt,"answer": answer}
#     except Exception as e:
#       raise HTTPException(status_code=500, detail=str(e))
#   else:
#     raise HTTPException(status_code=400, detail="Model not supported")