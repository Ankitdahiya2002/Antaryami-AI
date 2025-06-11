import streamlit as st
from src.auth import auth_page
from src.db import create_tables, save_chat, get_user_chats, get_user
from src.admin import show_admin_panel
from src.helper import ai_chat_response
from src.voice_input import get_voice_input
from src.translation import to_english, to_hindi

def show_user_panel():
    user_email = st.session_state["user"]
    user = get_user(user_email)
    user_name = user.get("name", "User")

    # Sidebar Welcome + Logout
    with st.sidebar:
        st.markdown(
            f"""
            <div style='
                background-color: #e0f7fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 10px;
                color: #333;
                font-weight: bold;
            '>
                👋 Hi, {user_name}
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚪 Logout", key="logout_btn"):
            del st.session_state["user"]
            st.rerun()

# Display user chats

    st.sidebar.title("⚙️ Settings")
    language = st.sidebar.selectbox("🌐 Language", ["English 🇺🇸", "Hindi🇮🇳"],index=0, disabled=True)


    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    response = None
    user_input = ""

    # 🎙️ Voice input trigger
    if st.button("🎙️ Start Listening"):
        voice_text = get_voice_input(language="hi-IN" if language == "Hindi" else "en-US",disabled =True)
        if voice_text:
            st.success(f"🎧 Heard: {voice_text}")
            user_input = voice_text
            auto_trigger = True
        else:
            auto_trigger = False
    else:
        auto_trigger = False

    # ✍️ Manual input (optional)
    with st.form("chat_form"):
        manual_input = st.text_input("Type your message here:")
        submitted = st.form_submit_button("Send")

    # Decide source of input
    if submitted and manual_input.strip():
        user_input = manual_input.strip()
        auto_trigger = True  # Treat like voice trigger

    # Process input if triggered
    if auto_trigger and user_input.strip():
        # Translate input to English if Hindi
        if language == "Hindi":
            translated_input = to_english(user_input)
        else:
            translated_input = user_input

        # Prepare context
        past_chats = get_user_chats(user_email)[-5:]
        history = ""
        for chat in past_chats:
            history += f"User: {chat['user_input'][:500]}\nAI: {chat['ai_response'][:500]}\n\n"

        prompt = history + f"User: {translated_input}\nAI:"

        with st.spinner("Thinking... 🤖"):
            response = ai_chat_response(prompt)

        if language == "Hindi":
            response = to_hindi(response)

        # Save and show
        st.session_state.chat_history.append({"user": user_input, "ai": response})
        save_chat(user_email, user_input, response, thread_id=None)
        st.success(f"🤖 {response}")

    # Show conversation history
    with st.expander("🕘 Conversation History", expanded=True):
        for chat in st.session_state.chat_history:
            st.markdown(f"**🧑 You:** {chat['user']}")
            st.markdown(f"**🤖 AI:** {chat['ai']}")
            st.markdown("---")


def main():
    st.set_page_config(page_title="OMNISNT AI Assistant", page_icon="🤖")
    create_tables()

    if "user" not in st.session_state:
        auth_page()
        return

    user = get_user(st.session_state["user"])
    if not user:
        st.error("User not found.")
        del st.session_state["user"]
        st.rerun()
        return

    if user.get("blocked"):
        st.error("Your account is blocked. Contact the administrator.")
        del st.session_state["user"]
        return

    if user.get("role") == "admin":
        show_admin_panel()
    else:
        show_user_panel()

if __name__ == "__main__":
    main()
