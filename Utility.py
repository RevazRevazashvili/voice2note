import math

from google.cloud import speech
from google.cloud import translate_v2 as translate
from openai import OpenAI
import os


def generate_audio_chunks(audio_data, chunk_duration=60):
        """
        Generator function to yield chunks of audio data that are 60 seconds or less in duration.

        Args:
        - audio_data: The complete audio data to be split into chunks.
        - chunk_duration: The duration of each audio chunk in seconds. Default is 60 seconds.

        Yields:
        - chunk: A chunk of audio data that is 60 seconds or less in duration.
        """
        # Calculate the number of samples per chunk
        samples_per_chunk = chunk_duration * 44100  # Adjust SAMPLE_RATE according to your audio sample rate

        # Calculate the total number of chunks needed
        total_chunks = math.ceil(len(audio_data) / samples_per_chunk)

        # Generate audio chunks
        for i in range(total_chunks):
            start_idx = i * samples_per_chunk
            end_idx = min((i + 1) * samples_per_chunk, len(audio_data))
            chunk = audio_data[start_idx:end_idx]
            yield chunk


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


class Recognizer:
    def __init__(self, service_account_file='key.json', language_code = 'ka', sample_rate_hertz= 44100, enable_automatic_punctuation= True):
        self.client = speech.SpeechClient.from_service_account_file(service_account_file)
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz= sample_rate_hertz,
            enable_automatic_punctuation= enable_automatic_punctuation,
            language_code= language_code
        )

    def transcribe_mp3_file(self, file):
        """
        transcribes mp3 file and returns transcript
        """
        with open(file, 'rb') as f:
            mp3_data = f.read()


        audio_file = speech.RecognitionAudio(content=mp3_data)

        response = self.client.recognize(
        config=self.config,
        audio=audio_file
        )

        transcripts = []

        for result in response.results:
            transcripts.append(result.alternatives[0].transcript)

        return transcripts

    def transcribe_from_audio_data(self, content):
        """Streams transcription of the given audio file."""
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in generate_audio_chunks(content)
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=self.config
        )

        # streaming_recognize returns a generator.
        responses = self.client.streaming_recognize(
            config=streaming_config,
            requests=requests,
        )

        data = []

        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. so first alternative will be the most likely one.
            for result in response.results:
                data.append(result.alternatives[0].transcript)

        return data

    def transcribe_streaming(self, stream_file: str) -> speech.RecognitionConfig:
        """Streams transcription of the given audio file."""

        with open(stream_file, "rb") as audio_file:
            content = audio_file.read()

        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in generate_audio_chunks(content)
        )

        streaming_config = speech.StreamingRecognitionConfig(config=self.config)

        # streaming_recognize returns a generator.
        responses = self.client.streaming_recognize(
            config=streaming_config,
            requests=requests,
        )

        data = []

        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. The other results will be for subsequent portions of
            # the audio.
            for result in response.results:
                print(f"Finished: {result.is_final}")
                print(f"Stability: {result.stability}")
                alternatives = result.alternatives
                data.append(alternatives[0].transcript)
                # The alternatives are ordered from most likely to least.
                for alternative in alternatives:
                    print(f"Confidence: {alternative.confidence}")
                    print(f"Transcript: {alternative.transcript}")

        return data


class Translator:
    def __init__(self, service_account_json='key.json'):
        self.client = translate.Client.from_service_account_json(service_account_json)

    def translate_text(self, text, target: str = 'en'):
        """
        translates text to target language
        :param text:
            -string or sequence of strings
        :param target:
            -target language code
        :return:
            -returns translated string regardless if input text is sequence of strings or just one string
        """
        # if text is str:
        #     text = text.decode("utf-8")
        # else:
        #     for txt in text:
        #         txt = txt.decode("utf-8")

        results = self.client.translate(text, target_language=target)

        # if not isinstance(results, list):
        #     return results

        try:
            translation = ""

            for result in results:
                translation += result["translatedText"]

            return translation
        except:
            # if its string then we just return it
            return results["translatedText"]


class Notetaker:
    def __init__(self, system_prompt_file="Prompts/SystemPrompt", api_key=None):
        #if api_key is None:
            #api_key = os.environ["OPENAI_API_KEY"]

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





# rec = Recognizer()
# trans = Translator()
# noter = Notetaker()
#
# transcripts = rec.transcribe_streaming("sounds/Recording123.mp3")
# translations = trans.translate_text(transcripts)
#
# text = ""
# for translation in translations:
#     text += translation
#
# finalNotes = noter.noterize(text)
#
# print(f"transcripts: {transcripts}")
# print(f"translations: {translations}")
# print(f"Notes: {finalNotes}")




