import streamlit as st
import os
import tempfile
import librosa
import soundfile as sf

# Voice pitch map (in semitones)
pitch_map = {
    "Man to Woman": 4,
    "Woman to Man": -4,
    "Child Girl to Child Boy": -1,
    "Child Boy to Child Girl": 1,
    "Child to Big Adult": -6,
}

# Properly fixed pitch shift function (librosa 0.10+ compatible)
def shift_pitch_librosa(input_path, output_path, n_steps):
    y, sr = librosa.load(path=input_path, sr=None)
    y_shifted = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=n_steps)
    sf.write(output_path, y_shifted, sr)

# Streamlit UI
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

    st.subheader("🎧 Original Audio")
    st.audio(temp_path)

    try:
        output_path = os.path.join(tempfile.gettempdir(), "converted_voice.wav")
        shift_pitch_librosa(temp_path, output_path, pitch_map[voice_style])
    except Exception as e:
        st.error("❌ Conversion failed.")
        st.exception(e)
        st.stop()

    st.subheader("✅ Converted Audio")
    st.audio(output_path)
    with open(output_path, "rb") as f:
        st.download_button("⬇️ Download WAV", f, file_name="converted_voice.wav")
