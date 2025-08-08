import streamlit as st
import wikipedia
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO
import requests

st.set_page_config(page_title="🎤📚 Wikipedia Chatbot", layout="centered")
st.title("🎤📚 Wikipedia Chatbot")

# Session to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🧹 Clear chat
if st.button("🧹 Clear History"):
    st.session_state.messages = []

# 🧠 Wikipedia fetch
def get_wikipedia_data(query):
    try:
        results = wikipedia.search(query)
        if not results:
            return "Sorry, I couldn't find anything on that topic.", None, None

        title = results[0]
        summary = wikipedia.summary(title, sentences=2)
        page = wikipedia.page(title)
        
        # Try fetching a good image
        image_url = None
        for img in page.images:
            if img.lower().endswith(('.jpg', '.png', '.jpeg')) and 'wiki' not in img.lower():
                image_url = img
                break

        return summary, page.url, image_url
    except wikipedia.DisambiguationError as e:
        return f"Too many meanings. Try more specific term. Options: {', '.join(e.options[:5])}", None, None
    except Exception as e:
        return f"Error: {str(e)}", None, None

# 🔊 Voice Output
def speak_text(text):
    tts = gTTS(text)
    fp = BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format='audio/mp3')

# 🎙️ Voice Input
def listen_to_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Please speak clearly.")
        audio = r.listen(source, phrase_time_limit=5)
    try:
        text = r.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.warning("Sorry, I could not understand your voice.")
    except sr.RequestError:
        st.error("Network error. Try again.")
    return ""

# 📝 Choose input type
st.subheader("Select Input Method")
input_mode = st.radio("Choose:", ["📝 Type", "🎤 Speak"])

user_input = ""

if input_mode == "📝 Type":
    user_input = st.text_input("Type your question:")
elif input_mode == "🎤 Speak":
    if st.button("🎙️ Start Voice Input"):
        user_input = listen_to_voice()

# Process the input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    summary, link, image_url = get_wikipedia_data(user_input)
    st.session_state.messages.append({"role": "bot", "content": summary})

    # Voice output
    speak_text(summary)

    # Image display
    if image_url:
        st.image(image_url, caption="📷 Wikipedia Image")

# Display chat history
st.subheader("Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {msg['content']}")