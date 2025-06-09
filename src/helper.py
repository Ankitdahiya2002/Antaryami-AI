import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

# Gemini AI Setup
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
print("GEMINI_API_KEY =", GEMINI_API_KEY)
print("Loaded GEMINI_API_KEY:", bool(GEMINI_API_KEY))

try:
    import google.generativeai as genai
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env file.")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print("❌ Failed to configure Gemini:", e)
    genai = None


def gemini_model_object(user_input):
    if not genai:
        return "Gemini is not properly configured. Check API key or SDK."
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content({
            "parts": [
                {"text": user_input}
            ]
        })
        return response.text
    except Exception as e:
        return f"Error from Gemini API: {str(e)}"



def ai_chat_response(user_input: str) -> str:
    """
    Wraps the AI response for external use.
    """
    return gemini_model_object(user_input)


def send_email(to_email, subject, body):
    """
    Send an email using SMTP credentials.
    """
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        print("Email credentials are not fully set.")
        return False

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, [to_email], msg.as_string())
        server.quit()
        print("✅ Email sent successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    test_input = "Hello, how are you?"
    print("AI Response:", ai_chat_response(test_input))
