import streamlit as st
import wikipedia
from gtts import gTTS
from io import BytesIO
import requests

st.set_page_config(page_title="🎤📚 Wikipedia Chatbot", layout="centered")
st.title("🎤📚 Wikipedia Chatbot"
)
if "messages" not in st.session_state:
    st.session_state.messages = []


if st.button("🧹 Clear History"):
    st.session_state.messages = []

def get_wikipedia_data(query):
    try:
        results = wikipedia.search(query)
        if not results:
            return "Sorry, I couldn't find anything on that topic.", None, None

        title = results[0]
        summary = wikipedia.summary(title, sentences=2)
        page = wikipedia.page(title)
        
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

def speak_text(text):
    tts = gTTS(text)
    fp = BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format='audio/mp3')

st.subheader("Ask Something")
user_input = st.text_input("Type your question:")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    summary, link, image_url = get_wikipedia_data(user_input)
    st.session_state.messages.append({"role": "bot", "content": summary})

    
    speak_text(summary)

    if image_url:
        st.image(image_url, caption="📷 Wikipedia Image")

st.subheader("Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {msg['content']}")
