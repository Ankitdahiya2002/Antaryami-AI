import streamlit as st

import os


from src.auth import auth_page
from src.db import create_tables, save_chat
from src.helper import ai_chat_response

def main():
    st.set_page_config(page_title="Antaryami AI Assistant", page_icon="🤖")

    create_tables()  # Ensure DB tables exist

    if "user" not in st.session_state:
        auth_page()
    else:
        user_email = st.session_state.user
        st.sidebar.write(f"Logged in as: {user_email}")

        if st.sidebar.button("Logout"):
            del st.session_state["user"]
            st.rerun()


        st.title("Welcome to Antaryami AI Assistant")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        with st.form(key="chat_form"):
            user_input = st.text_input("Type your message here:", key="input")
            submit = st.form_submit_button("Send")

        if submit and user_input:
            # Get AI response
            response = ai_chat_response(user_input)

            # Append to chat history (user and AI)
            st.session_state.chat_history.append({"user": user_input, "ai": response})

            # Save chat in DB
            save_chat(user_email, user_input, response, thread_id=None)

            # Don't reset st.session_state.input here to avoid error
    

        # Display chat history
        for chat in st.session_state.chat_history:
            st.markdown(f"**You:** {chat['user']}")
            st.markdown(f"**AI:** {chat['ai']}")
            
       


if __name__ == "__main__":
    main()
