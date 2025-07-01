import streamlit as st
import requests
from datetime import datetime

# Page setup
st.set_page_config(
    page_title="🧵 TailorTalk Assistant",
    page_icon="🧠",
    layout="centered"
)

# Custom styles
st.markdown("""
<style>
    @keyframes blink {
    0% {opacity: 0;}
    50% {opacity: 1;}
    100% {opacity: 0;}
    }
    .dots::after {
    content: "...";
    animation: blink 1.2s infinite;
    }
    body {
        background-color: #1e1e1e;
        color: #7c3aed;
    }
    .stApp {
        background-color: #1e1e1e;
        color: #7c3aed;
    }
    .stChatMessage.user {
        background-color: #2a2a2a;
        color: #7c3aed;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage.assistant {
        background-color: #333333;
        color: #7c3aed;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .title {
        font-size: 30px;
        font-weight: bold;
        color: #7c3aed;
        text-align: center;
        margin-bottom: 20px;
    }
    .css-1v0mbdj, .css-12oz5g7, .block-container {
        background-color: #1e1e1e !important;
        color: #7c3aed !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar (Assistant Info)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=100)
    st.markdown("### 🧵 TailorBot", unsafe_allow_html=True)
    st.write("Your smart calendar assistant.")
    st.write("Book, check, or cancel meetings using natural language.")
    st.markdown("---")
    st.write("🧠 Powered by LangGraph + Ollama (phi3)")
    #st.write("💬 Styled like ChatGPT dark mode")


# Title
st.markdown("<div class='title'>🧵 TailorTalk Calendar Assistant</div>", unsafe_allow_html=True)

# Chat state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input from user
user_input = st.chat_input("Ask me to check or book a meeting...")

if user_input:
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Send request to FastAPI
    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("TailorBot is typing<span class='dots'>.</span>", unsafe_allow_html=True)

        try:
            res = requests.post("http://127.0.0.1:8000/chat", json={"message": user_input})
            reply = res.json().get("reply", "⚠️ Something went wrong.")
        except Exception as e:
            reply = f"❌ Connection error: {e}"

        typing_placeholder.empty()  # clear loading dots
        st.markdown(reply)

    # Store and display assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

    # ✅ Optional: Show buttons if reply contains "Want to book" or "confirm"
    if "confirm" in reply.lower() or "want to book" in reply.lower():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes"):
                # Send yes message to FastAPI
                user_input = "Yes, confirm booking"
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)

                res = requests.post("http://127.0.0.1:8000/chat", json={"message": user_input})
                reply = res.json().get("reply", "⚠️ Failed again.")
                st.session_state.messages.append({"role": "assistant", "content": reply})
                with st.chat_message("assistant"):
                    st.markdown(reply)
        with col2:
            if st.button("❌ No"):
                st.write("Okay! Let me know if you'd like to try a different time.")

st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
