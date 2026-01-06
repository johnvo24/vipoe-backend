from google import genai
from app.core.config import settings


class Gemini:
    def __init__(self, api_key: str):
        self.name = "gemini-2.5-flash"
        self.client = genai.Client(api_key=api_key)

    def __generate__(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.name,
            contents=prompt,
        )
        return response.text


GEMINI_INSTANCE = Gemini(api_key=settings.GEMINI_API_KEY)
