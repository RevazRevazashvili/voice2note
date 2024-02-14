import streamlit as st
import requests
from googletrans import Translator
import openai
from st_audiorec import st_audiorec

api_key =

openai.api_key = api_key

st.title("ლექციის ჩანაწერები")
st.write('\n')

audio_file = st.file_uploader("ატვირთეთ ხმოვანი ფაილი", type=['wav', 'mp3', 'm4a'])

if audio_file:
    st.markdown(":green[ფაილი წარმატებით აიტვირთა]")


st.write("ან")

st.markdown('''<style>.css-1egvi7u {margin-top: -3rem;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.stAudio {height: 45px;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.css-v37k9u a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)  # darkmode
st.markdown('''<style>.css-nlntq9 a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)  # lightmode


st.write('ჩაწერეთ ხმა')

wav_audio_data = st_audiorec()

col_info, col_space = st.columns([0.57, 0.43])

if wav_audio_data is not None:
    col_playback, col_space = st.columns([0.58, 0.42])
    with col_playback:
        st.audio(wav_audio_data, format='audio/wav')

if wav_audio_data:
    st.markdown(":green[აუდიო წარმატებით ჩაიწერა]")


butt = st.button("გააანალიზე")


API_URL = "https://api-inference.huggingface.co/models/m3hrdadfi/wav2vec2-large-xlsr-georgian"
headers = {"Authorization": "Bearer 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"}


def query(data):
    resp = requests.post(API_URL, headers=headers, data=data)
    return resp.json()


def voice_to_text(audio):
    output = query(audio)
    output = next(iter(output.values()))
    return output


def translator_lan(text_to_translate, lang_from, lang_to):
    translator = Translator()
    translation = translator.translate(text_to_translate, src=lang_from, dest=lang_to)
    return translation.text


text = None
translated = ""

if audio_file:
    text = voice_to_text(audio_file)
    translated = translator_lan(text, "ka", "en")
else:
    text = voice_to_text(wav_audio_data)
    translated = translator_lan(text, "ka", "en")


translated = translated+"\ncan u write note from this text_to_translate?"


if butt:
    with st.spinner(text='მიმდინარეობს მონაცემთა ანალიზი…'):
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

    noted = translator_lan(note, "en", "ka")

    st.write(noted)
