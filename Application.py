import streamlit as st
import Realtime
import Utility
import os


butt = None
down = None
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
    if audio_file:
        st.markdown(":green[ფაილი წარმატებით აიტვირთა]")

    if audio_file:
        with st.spinner(text='მიმდინარეობს აუდიო ფაილის დამუშავება...'):
            text = rec.transcribe_from_audio_data(audio_file.read())
            translation = trans.translate_text(text)

        if butt is None:
            butt = st.button("გააანალიზე")

elif sound_mode == record:
    Realtime.sound_recorder()
    #st.write(wav_audio_data)
    #text = rec.transcribe_from_audio_data(wav_audio_data)
    #translated = trans.translate_text(text)
    #TODO: assign translation




if butt:
    if translation:
        with st.spinner(text='მიმდინარეობს ჩანაწერების ანალიზი...'):
            noted = noter.noterize(translation)
        noted = trans.translate_text(noted, target='ka')
        st.write(noted)
        st.download_button('Download', noted, file_name="Notes.txt")
