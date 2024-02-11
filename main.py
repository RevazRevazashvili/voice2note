import requests
from googletrans import Translator
from openai import OpenAI

client = OpenAI(
    api_key= 
)

API_URL = "https://api-inference.huggingface.co/models/m3hrdadfi/wav2vec2-large-xlsr-georgian"
headers = {"Authorization": "Bearer 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"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

output = query("sounds/Recording.mp3")

translator = Translator()
translation = translator.translate(output, dest="en")

print(translation.text)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "write me notes from this text",
        }
    ],
    model="gpt-3.5-turbo",
)
print(chat_completion)
