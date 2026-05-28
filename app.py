import streamlit as st
import ollama
from datetime import datetime
from pypdf import PdfReader

st.set_page_config(page_title="Prismora AI", page_icon="🤖")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

with st.sidebar:
    st.title("⚙️ Prismora AI")
    st.write("Local AI chatbot using Ollama + Streamlit")

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf is not None:
        reader = PdfReader(uploaded_pdf)
        pdf_text = ""

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text + "\n"

        st.session_state.pdf_text = pdf_text
        st.success("PDF uploaded successfully!")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    chat_history = ""
    for msg in st.session_state.messages:
        chat_history += f"{msg['role'].upper()}: {msg['content']}\n\n"

    st.download_button(
        label="Download Chat",
        data=chat_history,
        file_name="prismora_chat.txt",
        mime="text/plain"
    )

    st.markdown("---")
    st.write("Model: llama3.2")
    st.write("Status: Running locally")

st.title("🤖 Prismora AI Chatbot")

with open("knowledge.txt", "r", encoding="utf-8") as file:
    knowledge = file.read()

SYSTEM_PROMPT = f"""
You are Prismora AI, a friendly student assistant.

Rules:
- Answer simply and clearly.
- Use a friendly tone.
- Help with Python, AI, web development, and student doubts.
- If a PDF is uploaded, answer using the PDF content.
- If the question is about Prismora AI, use the knowledge below.
- If the answer is not in the PDF or knowledge, answer normally.

Knowledge:
{knowledge}

PDF Content:
{st.session_state.pdf_text}
"""

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "time" in message:
            st.caption(message["time"])

user_input = st.chat_input("Ask Prismora AI...")

if user_input:
    current_time = datetime.now().strftime("%H:%M")

    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "time": current_time
    })

    with st.chat_message("user"):
        st.write(user_input)
        st.caption(current_time)

    with st.chat_message("assistant"):
        with st.spinner("Prismora is reading and thinking..."):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            messages += st.session_state.messages

            response = ollama.chat(
                model="llama3.2",
                messages=messages
            )

            bot_reply = response["message"]["content"]
            st.write(bot_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply,
        "time": datetime.now().strftime("%H:%M")
    })