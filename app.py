import sys
import types
sys.modules['pyaudioop'] = types.SimpleNamespace()

import streamlit as st
from pydub import AudioSegment
import os
import tempfile
import platform

# Detect OS
current_os = platform.system()

# Optional local ffmpeg setup
USE_LOCAL_BINARIES = os.path.exists("ffmpeg")

if USE_LOCAL_BINARIES:
    if current_os == "Windows":
        ffmpeg_path = os.path.join("ffmpeg", "ffmpeg.exe")
        ffprobe_path = os.path.join("ffmpeg", "ffprobe.exe")
    else:
        ffmpeg_path = os.path.join("ffmpeg", "ffmpeg")
        ffprobe_path = os.path.join("ffmpeg", "ffprobe")

    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path
    st.write(f"🔧 Using local ffmpeg: `{ffmpeg_path}`")
else:
    st.write("ℹ️ Using system-installed ffmpeg/ffprobe")

# Pitch map
pitch_map = {
    "Man to Woman": 4,
    "Woman to Man": -4,
    "Baby Voice": 6,
    "Deep Voice": -6
}

def change_pitch(audio_segment, semitones):
    new_rate = int(audio_segment.frame_rate * (2.0 ** (semitones / 12.0)))
    pitched = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_rate})
    return pitched.set_frame_rate(44100)

# UI
st.set_page_config(page_title="🎙️ Voice Changer AI")
st.title("🎙️ Voice Changer AI")
st.markdown("Upload an MP3 or WAV, apply a voice style, and download the converted MP3.")

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
        st.error("❌ Could not load audio. Ensure ffmpeg and ffprobe are available.")
        st.exception(e)
        st.stop()

    st.subheader("🎧 Original Audio")
    st.audio(temp_path)

    shifted = change_pitch(audio, pitch_map[voice_style])
    output_path = os.path.join(tempfile.gettempdir(), "converted_voice.mp3")

    try:
        shifted.export(output_path, format="mp3")
    except Exception as e:
        st.error("❌ Could not export MP3. Check ffmpeg binary and permissions.")
        st.exception(e)
        st.stop()

    st.subheader("✅ Converted MP3")
    st.audio(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download MP3", f, file_name="converted_voice.mp3")
