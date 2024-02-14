import streamlit as st
from st_audiorec import st_audiorec

st.set_page_config(page_title="streamlit_audio_recorder")

st.markdown('''<style>.css-1egvi7u {margin-top: -3rem;}</style>''',
            unsafe_allow_html=True)

st.markdown('''<style>.stAudio {height: 45px;}</style>''',
            unsafe_allow_html=True)

st.markdown('''<style>.css-v37k9u a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)  # darkmode
st.markdown('''<style>.css-nlntq9 a {color: #ff4c4b;}</style>''',
            unsafe_allow_html=True)  # lightmode


def audiorec_demo_app():
    st.title('streamlit audio recorder')
    st.write('\n\n')

    wav_audio_data = st_audiorec()

    col_info, col_space = st.columns([0.57, 0.43])

    if wav_audio_data is not None:
        # display audio data as received on the Python side
        col_playback, col_space = st.columns([0.58, 0.42])
        with col_playback:
            st.audio(wav_audio_data, format='audio/wav')

#
if __name__ == '__main__':
    # call main function
    audiorec_demo_app()