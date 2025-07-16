import streamlit as st
from pydub import AudioSegment
import os
import tempfile

# 👇 Path to bundled ffmpeg (Windows: use "ffmpeg.exe")
ffmpeg_path = os.path.join("ffmpeg", "ffmpeg")
AudioSegment.converter = ffmpeg_path

# 🔊 Define pitch shift
pitch_map = {
    "Man to Woman": 4,
    "Woman to Man": -4,
    "Baby Voice": 6,
    "Deep Voice": -6
}

def change_pitch(audio_segment, semitones):
    new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (semitones / 12.0)))
    pitched = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
    return pitched.set_frame_rate(44100)

# 🚀 UI
st.set_page_config(page_title="🎙️ Voice Changer AI")
st.title("🎙️ Voice Changer AI")
st.markdown("Upload MP3 or WAV, apply a voice style, and download as MP3.")

uploaded_file = st.file_uploader("Upload audio", type=["mp3", "wav"])
voice_style = st.selectbox("Voice Style", list(pitch_map.keys()))

if uploaded_file:
    suffix = ".mp3" if uploaded_file.name.endswith(".mp3") else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    try:
        # Load with ffmpeg
        audio = AudioSegment.from_file(temp_path)
    except Exception as e:
        st.error("❌ Could not load audio. Ensure ffmpeg is working.")
        st.stop()

    st.subheader("🎧 Original Audio")
    st.audio(temp_path)

    shifted = change_pitch(audio, pitch_map[voice_style])

    # Export as MP3
    output_path = os.path.join(tempfile.gettempdir(), "converted_voice.mp3")
    try:
        shifted.export(output_path, format="mp3")
    except Exception as e:
        st.error("❌ Export failed. Is ffmpeg executable?")
        st.stop()

    st.subheader("✅ Converted Audio")
    st.audio(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download MP3", f, file_name="converted_voice.mp3")
