from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyAgXB06w08m37ur2l2gOJqJ-pzrqgQLCwE")

response = client.models.generate_content(
    model="gemini-2.0-flash-exp", contents="Explain how AI works in a few words"
)
print(response.text)