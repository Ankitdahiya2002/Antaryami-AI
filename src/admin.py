import streamlit as st
from src.db import get_all_users, block_user, export_chats_to_csv, count_registered_users


def show_admin_panel():
    st.title("👑 OMNISCENT Admin Dashboard")

    # Metrics
    total_users = count_registered_users()
    st.metric("Total Registered Users", total_users)

    st.markdown("---")

    # Search bar
    search_term = st.text_input("🔍 Search user by email or name")

    # User list
    st.subheader("📋 User Accounts")

    users = get_all_users()
    users = sorted(users, key=lambda u: u["blocked"], reverse=True)  # Show blocked users first

    if search_term:
        users = [
            u for u in users if
            search_term.lower() in u["email"].lower() or
            search_term.lower() in u.get("name", "").lower()
        ]

    if not users:
        st.info("No users found.")
    else:
        for user in users:
            col1, col2, col3 = st.columns([3, 1.2, 1])
            with col1:
                st.markdown(f"""
                    **{user.get("name", "Unnamed")}**  
                    📧 `{user['email']}`  
                    🧑‍💼 *{user.get("profession", "Unknown")}*  
                    🛡️ Role: `{user.get("role", "user")}`
                """)

            with col2:
                blocked = bool(user.get("blocked", 0))
                btn_label = "🔓 Unblock" if blocked else "🔒 Block"
                btn_color = "secondary" if blocked else "danger"
                if st.button(btn_label, key="block_" + user["email"]):
                    block_user(user["email"], not blocked)
                    st.success(f"{'Unblocked' if blocked else 'Blocked'} {user['email']}")
                    st.experimental_rerun()

            with col3:
                pass  # Reserved for future admin actions (e.g., delete, promote, etc.)

    st.markdown("---")

    # Export all chats
    st.subheader("📤 Export All Chat Logs")
    if st.button("Generate CSV"):
        csv_data = export_chats_to_csv()
        st.download_button("Download chat_history.csv", csv_data, "chat_history.csv", mime="text/csv")
