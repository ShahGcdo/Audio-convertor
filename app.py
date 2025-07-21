import sys
import types
import streamlit as st
from pydub import AudioSegment
import os
import tempfile

# ✅ Streamlit Cloud uses system ffmpeg/ffprobe — no custom paths needed

# Voice pitch map
pitch_map = {
    "Man to Woman": 4,
    "Woman to Man": -4,
    "Child Girl to Child Boy": -1,
    "Child Boy to Child Girl": 1,
    "Child to Big Adult": -6,
}

def change_pitch(audio_segment, semitones):
    new_rate = int(audio_segment.frame_rate * (2.0 ** (semitones / 12.0)))
    pitched = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
    return pitched.set_frame_rate(44100)

# UI
st.set_page_config(page_title="🎙️ Voice Converter")
st.title("🎙️ Voice Converter")
st.markdown("Upload an MP3 or WAV file, apply a voice transformation, and download the result.")

uploaded_file = st.file_uploader("📤 Upload audio file", type=["mp3", "wav"])
voice_style = st.selectbox("🎚️ Select Voice Style", list(pitch_map.keys()))

if uploaded_file:
    suffix = ".mp3" if uploaded_file.name.endswith(".mp3") else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    try:
        audio = AudioSegment.from_file(temp_path)
    except Exception as e:
        st.error("❌ Could not load audio. Make sure ffmpeg/ffprobe are available.")
        st.exception(e)
        st.stop()

    st.subheader("🎧 Original Audio")
    st.audio(temp_path)

    try:
        shifted = change_pitch(audio, pitch_map[voice_style])
        output_path = os.path.join(tempfile.gettempdir(), "converted_voice.mp3")
        shifted.export(output_path, format="mp3")
    except Exception as e:
        st.error("❌ Conversion or export failed.")
        st.exception(e)
        st.stop()

    st.subheader("✅ Converted Audio")
    st.audio(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download MP3", f, file_name="converted_voice.mp3")
