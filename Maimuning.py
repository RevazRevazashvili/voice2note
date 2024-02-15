
import math
from google.cloud import speech
from google.cloud import translate_v2 as translate
from openai import OpenAI
from flask import Flask, render_template, request
import os
import miniaudio

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
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz= sample_rate_hertz,
            enable_automatic_punctuation= enable_automatic_punctuation,
            language_code= language_code)


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

    @staticmethod
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

    def transcribe_streaming(self, stream_file: str) -> speech.RecognitionConfig:
        """Streams transcription of the given audio file."""

        with open(stream_file, "rb") as audio_file:
            content = audio_file.read()

        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in Recognizer.generate_audio_chunks(content)
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



# if __name__ == '__main__':
#     app.run(debug=True)





rec = Recognizer()

print(rec.transcribe_streaming("sounds/Recording123.mp3"))


# audio_path = "sounds/Recording.mp3"
# target_sampling_rate = 16000  #the input audio will be resampled a this sampling rate
# n_channels = 1  #either 1 or 2
# waveform_duration = 1 #in seconds
# offset = 0 #this means that we read only in the interval [15s, duration of file]
#
# waveform_generator = miniaudio.stream_file(
#      filename = audio_path,
#      sample_rate = target_sampling_rate,
#      seek_frame = int(offset * target_sampling_rate),
#      frames_to_read = int(waveform_duration * target_sampling_rate),
#      output_format = miniaudio.SampleFormat.SIGNED16,
#      nchannels = n_channels)
#
# i = 0
# for waveform in waveform_generator:
#     i += 1
#     print(f"Waveform: {waveform}\n\n\nEndWaveform {i}")
#
