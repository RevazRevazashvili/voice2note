import requests
from googletrans import Translator
import openai

api_key = "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"

openai.api_key = api_key

API_URL = "https://api-inference.huggingface.co/models/m3hrdadfi/wav2vec2-large-xlsr-georgian"
headers = {"Authorization": "Bearer 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"}


def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    resp = requests.post(API_URL, headers=headers, data=data)
    print(type(resp))
    return resp.json()


def voice_to_text(file):
    output = query(file)
    output = next(iter(output.values()))
    return output


def translator_lan(text, lang_from, lang_to):
    translator = Translator()
    translation = translator.translate(text, src=lang_from, dest=lang_to)
    return translation.text

text = voice_to_text("sounds/gender.mp3")

translated = translator_lan(text, "ka", "en")

translated = translated+"\ncan u write note from this text_to_translate?"
print(translated)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": translated
        }
    ]
)

note = response['choices'][0]['message']['content']

print(note)
