import speech_recognition as sr

def get_voice_input(language="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio, language=language)
        except Exception as e:
            return f"❌ Error: {e}"
