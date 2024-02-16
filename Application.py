import streamlit as st
import Realtime
import Utility
import os


butt = None
down = None
sigismun = None
audio_file = None
rec = Utility.Recognizer()
trans = Utility.Translator()
noter = Utility.Notetaker(api_key=st.secrets["OPENAI_API_KEY"])

translation = None

st.image("icon.png")
st.title("Noterator")
st.write('\n')

upload = "ატვირთეთ ფაილი"
record = "ჩაიწერეთ ხმა"
sound_mode = st.selectbox("აირჩიეთ ერთ-ერთი", [upload, record])


if sound_mode == upload:
    audio_file = st.file_uploader("ატვირთეთ აუდიო ფაილი", type=['mp3'])
elif sound_mode == record:
    sigismun = Realtime.sound_recorder_fantasy_time()
    st.write(sigismun.raw_data)
    #Realtime.sound_recorder()
    #st.write(wav_audio_data)
    #text = rec.transcribe_from_audio_data(wav_audio_data)
    #translated = trans.translate_text(text)
    #TODO: assign translation


if audio_file:
    with st.spinner(text='მიმდინარეობს აუდიო ფაილის დამუშავება...'):
        text = rec.transcribe_from_audio_data(audio_file.read())
        translation = trans.translate_text(text)

    st.markdown(":green[ფაილი წარმატებით აიტვირთა]")

    if butt is None:
        butt = st.button("გააანალიზე")

if sigismun is not None:
    if butt is None:
        butt = st.button("გააანალიზე")

    content = sigismun.raw_data
    with st.spinner(text='მიმდინარეობს აუდიოს დამუშავება...'):
        text = rec.transcribe_from_audio_data(content)
        translation = trans.translate_text(text)

    st.markdown(":green[ფაილი წარმატებით აიტვირთა]")





# st.title("Audio Recorder")
# audio = audiorecorder("Click to record", "Click to stop recording")
#
# if len(audio) > 0:
#     # To play audio in frontend:
#     st.audio(audio.export().read())
#
#     # # To save audio to a file, use pydub export method:
#     # audio.export("audio.wav", format="wav")
#     #
#     # # To get audio properties, use pydub AudioSegment properties:
#     # st.write(f"Frame rate: {audio.frame_rate}, Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds")





if butt:
    if translation:
        with st.spinner(text='მიმდინარეობს ჩანაწერების ანალიზი...'):
            noted = noter.noterize(translation)
        noted = trans.translate_text(noted, target='ka')
        st.write(noted)
        st.download_button('Download', noted, file_name="Notes.txt")
