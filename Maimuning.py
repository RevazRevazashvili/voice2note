from google.cloud import speech
import json


# get key!!! motherfucker!!
client = speech.SpeechClient.from_service_account_file('key.json')

# woher mein recordings
file_name = "sounds/Recording.mp3"

# open file biatch
with open(file_name, 'rb') as f:
    mp3_data = f.read();

# recognize mein ballzz
audio_file = speech.RecognitionAudio(content=mp3_data)

# it can config and oxidize on my anus
config = speech.RecognitionConfig(
    sample_rate_hertz= 44100,
    enable_automatic_punctuation= True,
    language_code='ka'
)

# them m̶o̶m̶e̶n̶t̶ mommy of truth
response = client.recognize(
    config=config,
    audio=audio_file
)

# rezuuulltss!!!!
for result in response.results:
    print(result.alternatives[0].transcript)

