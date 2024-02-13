from google.cloud import speech
import json
from google.cloud import translate_v2 as translate


class Recognizer:
    def __init__(self, service_account_file='key.json', language_code = 'ka', sample_rate_hertz= 44100, enable_automatic_punctuation= True):
        self.client = speech.SpeechClient.from_service_account_file(service_account_file)
        self.config = speech.RecognitionConfig(
            sample_rate_hertz= sample_rate_hertz,
            enable_automatic_punctuation= enable_automatic_punctuation,
            language_code= language_code)

    def transcribe_mp3_file(self, file_path):
        """
        transcribes mp3 file and returns transcript
        """

        with open(file_path, 'rb') as f:
            mp3_data = f.read();

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


# rec = Recognizer();
# trans = Translator();
#
# transcript = rec.transcribe_mp3_file("sounds/Recording.mp3")
#
# print(f"transcripts: {transcript}")
#
# print(f"translations: {trans.translate_text(transcript)}")


