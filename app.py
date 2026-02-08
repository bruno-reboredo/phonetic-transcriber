"""Streamlit UI for the phonetic transcriber."""

from __future__ import annotations

import streamlit as st

from phonetic_transcriber import EnglishIPATranscriber


st.set_page_config(page_title="Phonetic Transcriber")

if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "output_text" not in st.session_state:
    st.session_state.output_text = ""

st.title("Phonetic Transcriber")
st.write("Convert English text to IPA")

uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
if uploaded_file is not None:
    st.session_state.input_text = uploaded_file.read().decode("utf-8")

st.text_area(
    "Input text",
    key="input_text",
    height=200,
    placeholder="Type or paste English text here...",
)

col_transcribe, col_clear = st.columns(2)

with col_transcribe:
    transcribe_clicked = st.button("Transcribe", use_container_width=True)

with col_clear:
    clear_clicked = st.button("Clear", use_container_width=True)

if clear_clicked:
    st.session_state.input_text = ""
    st.session_state.output_text = ""

if transcribe_clicked:
    if not st.session_state.input_text.strip():
        st.warning("Please enter some text to transcribe.")
    else:
        transcriber = EnglishIPATranscriber()
        st.session_state.output_text = transcriber.transcribe_text(
            st.session_state.input_text
        )

st.subheader("IPA Output")
if st.session_state.output_text:
    st.code(st.session_state.output_text, language="")
else:
    st.caption("Your IPA transcription will appear here.")
