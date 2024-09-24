import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
import os
import base64
import tempfile
import google.generativeai as genai





languages = {
        "English": "en",
        "Urdu": "ur",
        
    }
translations = {
        "en": {
            "greeting": "Hello",
            "ask":"Ask Your Query",
            "farewell": "Goodbye",
            "listenError": "I am unable to listen to you",
            "mainHeader":"Record your voice and Audio Sphere will answer your query",
            "sidebarHeader":"Audio Sphere takes your voice and provide response in your language",
            "serverError": "Sorry, Audio Sphere speech service is down"
            
        },
        "ur":
            {
                "greeting": "السلام علیکم",
                "ask":"بولیۓ",
             "farewell": "خیر ملاقات",
             "listenError":"آپ کی آواز واضح نہیں ہے",
             "mainHeader":'اپنی آواز کو ریکارڈ کریں اور آڈیو اسفیئر آپ کے سوال کا جواب دے گا۔',
             "sidebarHeader":'آڈیو اسفیئر آپ کی آواز لیتا ہے اور آپ کی زبان میں جواب فراہم کرتا ہے۔',
             "serverError":'معذرت، آڈیو اسفیئر اسپیچ سروس بند ہے۔'
        }
        
    }
lang_code="ur"
def main():

    st.sidebar.header("About AudioSphere", divider='rainbow')
    st.sidebar.write(f'''Audio Sphere It takes in your voice input and response in your language''')
    
    
    # st.sidebar.info(f'''Development process includes these steps.  
    # 1️⃣ Convert Voice into text, using Google's speech recognition API.  
    # 2️⃣ Give text to LLM (I used Gemini), and generate a response.
    # we can also fine-tune LLM for URDU for more accurate responses).  
    # 3️⃣ Convert LLM-generated text into URDU speech by using Google TTS API.  
    # And boom, 🚀 ''')
    
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    # Define available languages
    
    # Language selection
    selected_language = st.sidebar.selectbox("Choose your language", list(languages.keys()))

    # Display selected language
    st.sidebar.write(f"You selected: {selected_language}")
    
    

    # Get translations for the selected language
    lang_code = languages[selected_language]

    st.title("🎤 :blue[Audio Sphere] 💬🤖")
    st.subheader(translations[lang_code]["mainHeader"], divider='rainbow')

    

    

    recorder = audio_recorder(text=translations[lang_code]["ask"], icon_size="2x", icon_name="microphone-lines", key="recorder")

    if recorder is not None:
        
        with st.container():
            col1, col2 = st.columns(2)

            with col2:
                # Display the audio file
                st.header('🧑')                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                st.audio(recorder)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_recording:
                    temp_recording.write(recorder)
                    temp_recording_path = temp_recording.name
                
                # Convert audio file to text
                
                text = audio_to_text(temp_recording_path,lang_code)
                st.success( text)

                # Remove the temporary file
                os.remove(temp_recording_path)


        response_text = llmModelResponse(text,lang=selected_language)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Convert the response text to speech
                response_audio_html = response_to_audio(response_text,lang_code)

                st.header('🤖')
                st.markdown(response_audio_html, unsafe_allow_html=True)

                st.info(response_text)


def audio_to_text(temp_recording_path,lang):
    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_recording_path) as source:
        recoded_voice = recognizer.record(source)
        try:
            text = recognizer.recognize_google(recoded_voice, language=lang)
            return text
        except sr.UnknownValueError:
            return  translations[lang_code]["listenError"]
        except sr.RequestError:
            return translations[lang_code]["serverError"] 

def response_to_audio(text, lang):
    tts = gTTS(text=text, lang=lang)
    tts_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    tts.save(tts_audio_path)

    # Get the base64 string of the audio file
    audio_base64 = get_audio_base64(tts_audio_path)

    # Autoplay audio using HTML and JavaScript
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

# Function to encode the audio file to base64
def get_audio_base64(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    return base64.b64encode(audio_bytes).decode()

def llmModelResponse(text,lang="Urdu"):
    prompt = f"""Kindly answer this question in {lang} langauge. 
    Dont use any other language or chaaracters from other languages.
    Use some kind {lang} words in start and ending of your answer realted to question. 
    Keep your answer short. 
    You can also ask anything related to the topic in {lang}.
    if you dont know the answer or dont understand the question, 
    Respond with 'I did not get what you speak, please try again' in {lang}.
    Question: {text}"""

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    GEMINI_API_KEY = st.secrets['gemini']['GEMINI_API_KEY']

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)

    return response.text

if __name__ == "__main__":
    main()
