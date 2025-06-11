import streamlit as st
from src.auth import auth_page
from src.db import create_tables, save_chat, get_user_chats, get_user
from src.admin import show_admin_panel
from src.helper import ai_chat_response

def main():
    st.set_page_config(page_title="OMNISNT AI Assistant", page_icon="🤖")
    create_tables()

    if "user" not in st.session_state:
        auth_page()
        return

    user_email = st.session_state["user"]
    user = get_user(user_email)

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
        return

    # Sidebar
    with st.sidebar:
        st.success(f"🔐 Logged in as: `{user_email}`")
        if st.button("🚪 Logout"):
            del st.session_state["user"]
            st.rerun()

    # Title
    st.title("🤖 OMNISNT AI Assistant")
    st.subheader("💬 Ask anything...")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat form
    with st.form("chat_form"):
        user_input = st.text_input("Type your message here:")
        submitted = st.form_submit_button("Send")

    # Process message
    if submitted and user_input.strip():
        past_chats = get_user_chats(user_email)[-5:]  # Get last 5 for context
        history = ""
        for chat in past_chats:
            user_msg = chat['user_input'][:500]
            ai_msg = chat['ai_response'][:500]
            history += f"User: {user_msg}\nAI: {ai_msg}\n\n"

        prompt = history + f"User: {user_input}\nAI:"

        with st.spinner("Thinking... 🤖"):
            response = ai_chat_response(prompt)

        st.session_state.chat_history.append({"user": user_input, "ai": response})
        save_chat(user_email, user_input, response, thread_id=None)

    # Chat display
    with st.expander("🕘 Conversation History", expanded=True):
        for chat in st.session_state.chat_history:
            st.markdown(f"**🧑 You:** {chat['user']}")
            st.markdown(f"**🤖 AI:** {chat['ai']}")
            st.markdown("---")


if __name__ == "__main__":
    main()
