from google.cloud import speech
import json

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

        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)

        return transcripts



rec = Recognizer();

print(rec.transcribe_mp3_file("sounds/Recording.mp3"))


