import queue
import time
import os
import av
import ffmpeg
import pydub
import streamlit as st
from twilio.rest import Client
from google.cloud import speech

from streamlit_webrtc import WebRtcMode, webrtc_streamer

import Utility


@st.cache_data  # type: ignore
def get_ice_servers():
    """Using Twilios server as in https://github.com/whitphx/streamlit-stt-app"""

    # Ref: https://github.com/whitphx/streamlit-stt-app
    try:
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    except KeyError:
        return [{"urls": ["stun:stun.l.google.com:19302"]}]

    client = Client(account_sid, auth_token)

    token = client.tokens.create()

    return token.ice_servers


def sound_recorder():
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration={"iceServers": get_ice_servers()},
        media_stream_constraints={"video": False, "audio": True},
    )

    status_indicator = st.empty()

    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Loading...")
    text_output = st.empty()

    client = speech.SpeechClient.from_service_account_file("key.json")

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        enable_automatic_punctuation=True,
        language_code="en-US"
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    while True:
        if webrtc_ctx.audio_receiver:
            sound_chunk = pydub.AudioSegment.empty()
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            status_indicator.write("Running. Say something!")

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound

            if len(sound_chunk) > 0:
                sound_chunk = sound_chunk.set_channels(1).set_frame_rate(
                    44100
                )

                content = sound_chunk.raw_data

                # Create a generator to yield audio content for streaming recognition
                requests = (speech.StreamingRecognizeRequest(audio_content=content),)

                # Perform streaming recognition
                responses = client.streaming_recognize(
                    config=streaming_config,
                    requests=requests
                )

                # Process recognition responses
                for response in responses:
                    for result in response.results:
                        # Update the transcription text output
                        text_output.markdown(f"**Text:** {result.alternatives[0].transcript}")
        else:
            status_indicator.write("AudioReciver is not set. Abort.")
            break


def sound_recorder_v2():
    # Initialize WebRTC streamer
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration={"iceServers": get_ice_servers()},
        media_stream_constraints={"video": False, "audio": True},
    )

    status_indicator = st.empty()

    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Loading...")
    text_output = st.empty()

    client = speech.SpeechClient.from_service_account_json("key.json")

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,  # Adjust this according to your audio stream
        enable_automatic_punctuation=True,
        language_code="ka",  # Adjust the language code as needed
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True)

    while True:
        if webrtc_ctx.audio_receiver:
            status_indicator.write("Running. Say something!")
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            sound_chunk = pydub.AudioSegment.empty()

            for audio_frame in audio_frames:
                audio_segment = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += audio_segment

                # Convert to the required format (16-bit, 1 channel, 48kHz)

            sound_chunk = sound_chunk.set_frame_rate(48000).set_channels(1).set_sample_width(2)

            # Prepare audio content for streaming recognition
            content = sound_chunk.raw_data

            # Create a generator to yield audio content for streaming recognition
            requests = (speech.StreamingRecognizeRequest(audio_content=content),)

            # Perform streaming recognition
            responses = client.streaming_recognize(
                config=streaming_config,
                requests=requests
            )

            # Process recognition responses
            for response in responses:
                for result in response.results:
                    # Update the transcription text output
                    text_output.markdown(f"**Text:** {result.alternatives[0].transcript}")
        else:
            status_indicator.write("AudioReceiver is not set. Abort.")
            break


