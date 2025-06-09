import streamlit as st
from src.db import create_user, get_user
import bcrypt

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def auth_page():
    st.markdown(
        """
        <style>
        .auth-card {
            max-width: 400px;
            margin: 4rem auto;
            padding: 2rem;
            background: #f9f9f9;
            border-radius: 12px;
            box-shadow: 0 0 10px rgb(0 0 0 / 0.1);
        }
        .auth-header {
            text-align: center;
            font-weight: 600;
            font-size: 1.8rem;
            margin-bottom: 1rem;
            color: #333;
        }
        .link-btn {
            background: none;
            border: none;
            color: #1e90ff;
            cursor: pointer;
            font-weight: 500;
            text-decoration: underline;
            padding: 0;
            margin-top: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
    if "login_email" not in st.session_state:
        st.session_state.login_email = ""
    if "signup_email" not in st.session_state:
        st.session_state.signup_email = ""

    def switch_mode():
        st.session_state.auth_mode = "signup" if st.session_state.auth_mode == "login" else "login"

   # st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    if st.session_state.auth_mode == "login":
        st.markdown('<div class="auth-header">Sign In to Your Account</div>', unsafe_allow_html=True)

        email = st.text_input("Email", value=st.session_state.login_email, placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            if email and password:
                user = get_user(email)
                if user and not user["blocked"]:
                    stored_hash = user["password"]
                    # stored_hash is string, encode to bytes
                    if verify_password(password, stored_hash.encode('utf-8')):
                        st.success(f"Welcome back, {email}!")
                        st.session_state['user'] = email
                    else:
                        st.error("Incorrect password.")
                elif user and user["blocked"]:
                    st.error("Your account is blocked. Contact admin.")
                else:
                    st.error("User not found.")
            else:
                st.warning("Please enter both email and password.")

        st.button("New user? Sign Up", on_click=switch_mode, key="to_signup")

    else:  # Signup form
        st.markdown('<div class="auth-header">Create New Account</div>', unsafe_allow_html=True)

        new_email = st.text_input("Email", value=st.session_state.signup_email, placeholder="Enter your email")
        new_password = st.text_input("Password", type="password", placeholder="Enter password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")

        if st.button("Sign Up"):
            if new_email and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    hashed = hash_password(new_password)
                    created = create_user(new_email, hashed.decode('utf-8'))
                    if created:
                        st.success("Account created successfully! Please login.")
                        st.session_state.signup_email = ""
                        st.session_state.auth_mode = "login"
                    else:
                        st.error("Email already registered. Try login or use a different email.")
            else:
                st.warning("Please fill all fields.")

        st.button("Already have an account? Login", on_click=switch_mode, key="to_login")

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    auth_page()
