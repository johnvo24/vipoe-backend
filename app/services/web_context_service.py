from app.services.geminiai_service import Gemini
import re


def split_into_chunks(text: str, max_words: int = 1500) -> list[str]:
  words = re.findall(r'\S+', text)
  chunks = []
  for i in range(0, len(words), max_words):
    chunk = ' '.join(words[i:i + max_words])
    chunks.append(chunk.strip())
  return chunks

async def summarize_chunks(
  chunks: list[str],
  prompt: str,
  gemini: Gemini
) -> list[str]:
  summaries = []
  for i, chunk in enumerate(chunks):
    summar_prompt = f"""
Bạn là một AI đọc hiểu văn bản. Lược bỏ một phần thông tin không liên quan tới prompt sau ở trong [Văn bản] và chỉ trả về phần thông tin liên quan tới prompt trong văn bản dưới đây:

[Prompt]: "{prompt}"

[Văn bản]:
{chunk.strip()}

[Kết quả]:
"""
    try:
      summary = gemini.__generate__(summar_prompt).strip()
      summaries.append(summary)
    except Exception as e:
      print(f"[SummarizeChunk] Chunk {i} failed: {e}")
      continue
  return summaries

async def summarize_contexts_by_chunks(
  contexts_dict: dict,       # ← result
  prompt: str,
  gemini: Gemini
) -> list[dict]:
  final_summaries = []

  for i, context in enumerate(contexts_dict["contexts"]):
    chunks = split_into_chunks(text=context)
    summaries = await summarize_chunks(
      chunks=chunks,
      prompt=prompt,
      gemini=gemini
    )
    final_summaries.append({
      "source": contexts_dict["sources"][i],
      "summaries": summaries
    })

  return final_summaries