import streamlit as st
import Utility

first_run = None
butt = None
down = None
audio_file = None
rec = Utility.Recognizer()
trans = Utility.Translator()
noter = Utility.Notetaker()
translation = None

st.image("icon.png")
st.title("Noterator")
st.write('\n')

BUCKET_NAME = "noterator_bucket"
DESTINATION_BLOB_NAME = "uploaded-file.mp3"
CREDENTIALS_FILE = "key.json"

audio_file = st.file_uploader("ატვირთეთ აუდიო ფაილი", type=['mp3'])

if audio_file:
    st.markdown(":green[ფაილი წარმატებით აიტვირთა]")
    if butt is None:
        butt = st.button("გააანალიზე")


if butt:
    with st.spinner(text='მიმდინარეობს აუდიო ატვირთვა...'):
        path = Utility.upload_to_gcs(BUCKET_NAME, audio_file.read(), DESTINATION_BLOB_NAME, CREDENTIALS_FILE)
    with st.spinner(text='მიმდინარეობს აუდიო ფაილის დამუშავება...'):
        text = rec.transcribe_gcs(path)
        st.write(text)
        #text = rec.transcribe_from_audio_data(audio_file.read())
    with st.spinner(text='მიმდინარეობს ტრანსლაცია...'):
        translation = trans.translate_text(text)
     #text = rec.transcribe_gcs("gs://noterator_bucket/მერაბ მამარდაშვილი - I ლექცია, მეორე ნაწილი. 10II-1990 წ..mp3")
    if translation:
        st.write(translation)
        with st.spinner(text='მიმდინარეობს ჩანაწერების ანალიზი...'):
            noted = noter.noterize(translation)
        noted = trans.translate_text(noted, target='ka')
        st.write(noted)
        first_run = None
        st.download_button('Download', noted, file_name="Notes.txt")
        butt = None
