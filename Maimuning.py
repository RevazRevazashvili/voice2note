from google.cloud import speech
from google.cloud import translate_v2 as translate
from openai import OpenAI
from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"


    rec = Recognizer();
    trans = Translator();
    noter = Notetaker();

    transcripts = rec.transcribe_mp3_file(file)
    translations = trans.translate_text(transcripts)

    text = ""
    for translation in translations:
        text += translation;

    finalNotes = noter.noterize(text)

    print(f"transcripts: {transcripts}")
    print(f"translations: {translations}")
    print(f"Notes: {finalNotes}")

    return render_template('index.html', transcripts=transcripts, translations=translations, notes=finalNotes)

class Recognizer:
    def __init__(self, service_account_file='key.json', language_code = 'ka', sample_rate_hertz= 44100, enable_automatic_punctuation= True):
        self.client = speech.SpeechClient.from_service_account_file(service_account_file)
        self.config = speech.RecognitionConfig(
            sample_rate_hertz= sample_rate_hertz,
            enable_automatic_punctuation= enable_automatic_punctuation,
            language_code= language_code)

    def transcribe_mp3_file(self, file):
        """
        transcribes mp3 file and returns transcript
        """

        mp3_data = file.read();

        audio_file = speech.RecognitionAudio(content=mp3_data)

        response = self.client.recognize(
        config=self.config,
        audio=audio_file
        )

        transcripts = []

        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)

        return transcripts

class Translator:
    def __init__(self, service_account_json='key.json'):
        self.client = translate.Client.from_service_account_json(service_account_json)

    def translate_text(self, text: str, target: str = 'en'):
        """
        translates test to target language
        """
        if isinstance(text, bytes):
            text = text.decode("utf-8")

        # Text can also be a sequence of strings, in which case this method
        # will return a sequence of results for each text.
        results = self.client.translate(text, target_language=target)

        # print("Text: {}".format(result["input"]))
        # print("Translation: {}".format(result["translatedText"]))
        # print("Detected source language: {}".format(result["detectedSourceLanguage"]))

        translations = []

        for result in results:
            translations.append(result["translatedText"])

        return translations

def read_text_file(file_path):
        """
        reads text from file and returns it in a string form
        :param file_path: path of the file
        :return: text of the file parsed as a string
        """
        try:
            with open(file_path, 'r') as file:
                text = file.read()
                return text
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None

class Notetaker:
    def __init__(self, system_prompt_file="Prompts/SystemPrompt", api_key = None):
        if api_key == None:
            api_key = os.environ['OPENAI_API_KEY']

        self.client = OpenAI(api_key=api_key)
        self.system_prompt = read_text_file(system_prompt_file)

    def noterize(self, text):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
            ]
        )

        return completion.choices[0].message.content



if __name__ == '__main__':
    app.run(debug=True)

