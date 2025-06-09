import streamlit as st
from src.db import get_all_users, block_user, export_chats_to_csv, count_registered_users


def show_admin_panel():
    st.subheader("👑 Admin Dashboard")

    # Show total users count
    total_users = count_registered_users()
    st.metric("Total Registered Users", total_users)

    st.markdown("---")
    st.markdown("### Users List")

    users = get_all_users()

    for user in users:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"{user['email']} ({user['role']})")
        with col2:
            blocked = bool(user['blocked'])
            if st.button("Unblock" if blocked else "Block", key=user['email']):
                block_user(user['email'], not blocked)
                st.experimental_rerun()
        with col3:
            pass  # Future: add more admin controls here

    st.markdown("---")
    if st.button("📤 Export All Chats as CSV"):
        csv_data = export_chats_to_csv()
        st.download_button("Download chat_history.csv", csv_data, "chat_history.csv", mime="text/csv")
