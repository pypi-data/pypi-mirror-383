import streamlit as st
from streamlit_audio_stream_player import audio_bar, audio_orb
import time

st.title("🎵 Audio Stream Visualizer Test")
# Audio stream options
stream_options = {
    "Radio Paradise (MP3)": "https://stream.radioparadise.com/mp3-128",
    "BBC World Service": "https://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
    "Custom URL": "custom"
}

selected_stream = st.selectbox("Select Audio Stream", list(stream_options.keys()))

if selected_stream == "Custom URL":
    stream_url = st.text_input("Enter Audio Stream URL", value="https://stream.radioparadise.com/mp3-128")
else:
    stream_url = stream_options[selected_stream]

mode = st.radio("Select Mode", ["bar", "orb"], horizontal=True)
# Display visualizer
if stream_url:
    if mode == "bar":
        st.write("Bar Visualizer")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            prime_color = st.color_picker("Prime Color", value="#00f5ff", key="c1_prime")
        with col2:
            second_color = st.color_picker("Second Color", value="#0a0e27", key="c1_second")
        audio_bar(
            data=stream_url,
            prime_color=prime_color,
            second_color=second_color,
            key="bar"
        )

    if mode == "orb":
        st.write("Orb Visualizer")
        col1, col2, col3 = st.columns(3)
        with col1:
            prime_color = st.color_picker("Prime Color", value="#ff006e", key="c2_prime")
        with col2:
            second_color = st.color_picker("Second Color", value="#8338ec", key="c2_second")
        with col3:
            seed = st.number_input("Select Seed", value=1000, key="c2_seed")
        audio_orb(
            data=stream_url,
            prime_color=prime_color,
            second_color=second_color,
            seed=seed,
            key="orb"
        )