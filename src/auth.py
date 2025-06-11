import streamlit as st
from src.db import create_user, get_user
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def auth_page():
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "login_email" not in st.session_state:
        st.session_state.login_email = ""
    if "signup_email" not in st.session_state:
        st.session_state.signup_email = ""

    def switch_mode():
        st.session_state.auth_mode = "signup" if st.session_state.auth_mode == "login" else "login"

    st.title("OMNISNT AI Assistant 🤖")

    if st.session_state.auth_mode == "login":
        email = st.text_input("Email", value=st.session_state.login_email)
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if email and password:
                user = get_user(email)
                if user:
                    if user["blocked"]:
                        st.error("Your account is blocked. Contact admin.")
                    elif verify_password(password, user["password"]):
                        st.success(f"Welcome back, {email}!")
                        st.session_state['user'] = email
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("User not found.")
            else:
                st.warning("Please enter both email and password.")

        st.button("New user? Sign Up", on_click=switch_mode)

    else:  # signup mode
            new_email = st.text_input("Email", value=st.session_state.signup_email)
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")

            name = st.text_input("Full Name")
            profession = st.text_input("Profession")
            if st.button("Sign Up"):
                if new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        hashed = hash_password(new_password)
                        created = create_user(new_email, hashed)
                        if created:
                            st.success("Account created! Please log in.")
                            st.session_state.auth_mode = "login"
                        else:
                            st.error("Email already registered.")
            else:
                    st.warning("Please fill all fields.")

            st.button("Already have an account? Login", on_click=switch_mode)
