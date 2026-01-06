from typing import List
import httpx, requests, trafilatura
from app.services.geminiai_service import Gemini

# === Crawl HTML and extract text ===
async def fetch_main_text(url: str, timeout=10.0, max_length=6000, min_length=300) -> str:
  try:
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
      resp = await client.get(url)
      if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", "").lower():
        html = resp.text
        content = trafilatura.extract(html)
        if content and len(content.strip()) >= min_length:
          return content.strip()[:max_length]
  except Exception as e:
    print(f"[fetch_main_text] {url} failed: {e}")
  return ""

# === Google Custom Search ===
def search_google_cse(query: str, api_key: str, cx: str, num=5) -> List[str]:
  try:
    resp = requests.get("https://www.googleapis.com/customsearch/v1", params={
      "q": query, "key": api_key, "cx": cx, "num": num
    }, timeout=10)
    resp.raise_for_status()
    return [item["link"] for item in resp.json().get("items", [])]
  except Exception as e:
    print(f"[GoogleCSE] '{query}' failed: {e}")
    return []

# === Multi-query RAG search ===
async def search_all_queries(queries: List[str], api_key: str, cx: str, max_urls: int = 5) -> dict:
  seen, urls = set(), []
  for q in queries:
    for url in search_google_cse(q, api_key, cx, num=3):
      if url not in seen:
        urls.append(url)
        seen.add(url)
      if len(urls) >= max_urls: break
    if len(urls) >= max_urls: break

  print(queries)
  print(urls)

  contexts, sources = [], []
  for url in urls:
    content = await fetch_main_text(url)
    if content:
      contexts.append(content)
      sources.append(url)

  return {"queries": queries, "contexts": contexts, "sources": sources}

# === Generate search queries from LLM ===
def generate_search_queries(prompt: str, gemini: Gemini, max_queries: int = 3) -> List[str]:
  instruction = f"""
Bạn là một trợ lý AI thông minh. Hãy viết {max_queries} truy vấn Google khác nhau, ngắn gọn, rõ ràng cho prompt sau:

"{prompt}"

Trả về dưới dạng danh sách và sắp xếp theo độ liên quan từ trên xuống dưới:
- ...
- ...
- ...
"""
  try:
    output = gemini.__generate__(instruction)
    return [
      line.lstrip("-•–— ").strip()
      for line in output.split("\n")
      if line.strip().startswith(("-", "•", "–", "—"))
    ][:max_queries] or [prompt]
  except Exception as e:
    print(f"[QueryGen] Gemini failed: {e}")
    return [prompt]

def build_prompt_with_context(
  prompt: str,
  summaries_data: list[dict],
  system_instruction: str = None,
  final_instruction: str = None
) -> str:
  if system_instruction is None:
    system_instruction = (
      "You are a professional Vietnamese poet. Your task is strictly limited to only two roles:\n"
      "1. Answer requests related to Vietnamese poetry using your expert knowledge or the provided summaries.\n"
      "2. Compose original Vietnamese poems if the user explicitly requests it.\n\n"
      "You may refer to the provided summaries as helpful sources, but you are not limited to them. "
      "You may also rely on your own professional knowledge of Vietnamese poetry.\n\n"
      "Do not answer any requests that are not related to Vietnamese poetry. "
      "If the request is irrelevant, politely refuse to answer. \n\n"
    )

  if final_instruction is None:
    final_instruction = (
      "Trả lời bằng tiếng Việt, với vai trò là một nhà thơ chuyên nghiệp. Xưng hô \"tớ\" và \"cậu\"."
      "Sử dụng thông tin từ phần tóm tắt bên trên, và ghi rõ nguồn dưới dạng ([1] https://..., ...) nếu như có trích dẫn chính xác nội dung. Nếu không trích dẫn thì không cần ghi nguồn. "
      "Yêu cầu người dùng được viết trong mục [User Request] ở trên. "
      "Nếu người dùng yêu cầu sáng tác thơ, bạn có thể tham khảo các phần tóm tắt bên trên như nguồn cảm hứng hoặc để đưa chi tiết thực tế vào bài thơ. "
      "Nếu yêu cầu của người dùng không liên quan tới lĩnh vực thơ ca hoặc văn học, hãy từ chối trả lời một cách lịch sự chỉ với câu trả lời sau: "
      "“Xin lỗi cậu, nội dung này nằm ngoài phạm vi xử lý của tớ rồi.”"
    )

  prompt_lines = []

  prompt_lines.append("[System Instruction]")
  prompt_lines.append(system_instruction.strip())
  prompt_lines.append("")

  prompt_lines.append("[Summarized Context from Vietnamese Sources]")
  for idx, item in enumerate(summaries_data):
    source = item.get("source", "Unknown Source")
    summaries = item.get("summaries", [])
    prompt_lines.append(f"\n--- Source [{idx + 1}]: {source}")
    for summary in summaries:
      summary = summary.strip()
      if summary:
        prompt_lines.append(f"- {summary}")

  prompt_lines.append("\n[Final Instruction]")
  prompt_lines.append(final_instruction.strip())

  prompt_lines.append("\n[User Request]")
  prompt_lines.append(prompt.strip())

  return "\n".join(prompt_lines)

def build_prompt_without_context(
  prompt: str,
  system_instruction: str = None,
  final_instruction: str = None
) -> str:
  if system_instruction is None:
    system_instruction = (
      "You are a professional Vietnamese poet. Your task is strictly limited to only two roles:\n"
      "1. Answer requests related to Vietnamese poetry using your expert knowledge or the provided summaries.\n"
      "2. Compose original Vietnamese poems if the user explicitly requests it.\n\n"
      "Use your own knowledge and creative ability. Do not answer unrelated topics. "
      "If the request is outside the scope of Vietnamese poetry, politely refuse to answer.\n\n"
    )

  if final_instruction is None:
    final_instruction = (
      "Trả lời bằng tiếng Việt với tư cách là một nhà thơ chuyên nghiệp. Xưng hô \"tớ\" và \"cậu\". "
      "Yêu cầu người dùng được viết trong mục [User Request] ở trên. "
      "Nếu người dùng yêu cầu sáng tác, hãy sáng tác một bài thơ tiếng Việt phù hợp. "
      "Nếu yêu cầu của người dùng không liên quan tới lĩnh vực thơ ca hoặc văn học, hãy từ chối trả lời một cách lịch sự chỉ với câu trả lời sau: "
      "“Xin lỗi cậu, nội dung này nằm ngoài phạm vi xử lý của tớ rồi.”"
    )

  prompt_lines = []

  prompt_lines.append("[System Instruction]")
  prompt_lines.append(system_instruction.strip())
  prompt_lines.append("")

  prompt_lines.append("\n[Final Instruction]")
  prompt_lines.append(final_instruction.strip())

  prompt_lines.append("[User Request]")
  prompt_lines.append(prompt.strip())

  return "\n".join(prompt_lines)


def build_edit_poem_prompt(
  prompt: str,
  system_instruction: str = None,
  final_instruction: str = None
) -> str:
  if system_instruction is None:
    system_instruction = (
      "You are a professional Vietnamese poetry editor and critic.\n"
      "\n"
      "Your task is strictly limited to analyzing Vietnamese lục bát poems provided by the user and detecting errors based on Vietnamese poetic rules and essential Vietnamese grammar only.\n"
      "\n"
      "You MUST:\n"
      "- Analyze the poem line by line.\n"
      "- Detect errors related to structure, rhyme, tone, meaning, or imagery.\n"
      "- Return exactly ONE correction step per response, strictly following the format defined in the Final Instruction.\n"
      "- Propose only the minimal word-, phrase-, or line-level replacement needed to fix that error.\n"
      "- Base all reasoning strictly on established Vietnamese lục bát rules.\n"
      "\n"
      "You MUST NOT:\n"
      "- Add explanations outside the required output format.\n"
      "- Fix multiple errors in one response.\n"
      "- Rewrite the entire poem.\n"
      "- Add any extra text before or after the required structure.\n"
    )

  if final_instruction is None:
    final_instruction = (
      "Các lỗi trong thơ lục bát bao gồm:\n"
      "- SE (Structural Error): Thơ lục bát gồm các cặp câu 6-8 chữ. Sai quy tắc này là lỗi cấu trúc.\n"
      "- RE (Rhyme Error): Tiếng cuối câu 6 – tiếng thứ 6 câu 8 – tiếng cuối câu 8 phải cùng vần.\n"
      "- TE (Tone Error):\n"
      "  + Thanh bằng: ngang, huyền\n"
      "  + Thanh trắc: sắc, hỏi, ngã, nặng\n"
      "  + Câu lục: tiếng 2-4-6 = B-T-B\n"
      "  + Câu bát: tiếng 2-4-6-8 = B-T-B-B (hoặc T-B-T-B)\n"
      "- ME (Meaning Error): Nội dung không rõ ràng, mâu thuẫn, hoặc lệch chủ đề.\n"
      "- IE (Imagery Error): Hình ảnh mơ hồ, khiên cưỡng, sáo rỗng, hoặc không gợi cảm xúc.\n"
      "\n"
      "BẮT BUỘC trả về kết quả theo đúng cấu trúc sau (không thêm, không bớt token):\n"
      "<error> error_type\n"
      "<desc> Mô tả lỗi và ảnh hưởng của nó.\n"
      "<reason> Lập luận chi tiết dựa trên luật thơ hoặc ngữ pháp.\n"
      "<action> Từ, cụm từ, hoặc câu thay thế\n"
      "<replace> Từ, cụm từ, hoặc câu cũ\n"
      "<line> Số dòng xảy ra lỗi\n"
      "<index> Vị trí của từ trong dòng (bắt đầu từ 1)\n"
      "<effect> Đánh giá tác động của việc sửa lỗi này đối với chất lượng bài thơ.\n"
      "<eois> HOẶC <eos>\n"
      "\n"
      "QUY TẮC KẾT THÚC:\n"
      "- Nếu sau bước sửa này bài thơ vẫn còn lỗi → kết thúc bằng <eois>\n"
      "- Nếu sau bước sửa này bài thơ đã hoàn chỉnh → kết thúc bằng <eos>\n"
      "\n"
      "TRƯỜNG HỢP ĐẶC BIỆT:\n"
      "- Nếu bài thơ hoàn toàn không có lỗi, chỉ trả về đúng một token:\n"
      "<eos>\n"
    )

  prompt_lines = []

  prompt_lines.append("[System Instruction]")
  prompt_lines.append(system_instruction.strip())
  prompt_lines.append("")

  prompt_lines.append("\n[Final Instruction]")
  prompt_lines.append(final_instruction.strip())

  prompt_lines.append("[Poem to Edit]")
  prompt_lines.append(prompt.strip())

  return "\n".join(prompt_lines)