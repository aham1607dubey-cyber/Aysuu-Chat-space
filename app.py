import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="ChatSpace",
    page_icon="💬",
    layout="wide"
)

# ---------- CSS ----------
st.markdown("""
<style>
    .stApp {
        background: #0b1020;
        color: white;
    }

    .title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #94a3b8;
        margin-bottom: 25px;
    }

    .chat-box {
        background: #111827;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
    }

    .message {
        background: #1e293b;
        padding: 12px 16px;
        border-radius: 15px;
        margin: 8px 0;
        width: fit-content;
        max-width: 75%;
    }

    .my-message {
        background: #2563eb;
        padding: 12px 16px;
        border-radius: 15px;
        margin: 8px 0 8px auto;
        width: fit-content;
        max-width: 75%;
    }

    .user-name {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 3px;
    }

    .online {
        color: #22c55e;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "user": "Alex",
            "message": "Hey! Welcome to ChatSpace 👋",
            "time": "Now"
        },
        {
            "user": "Alex",
            "message": "This is our first conversation.",
            "time": "Now"
        }
    ]


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 💬 ChatSpace")

    st.markdown("---")

    username = st.text_input(
        "Your name",
        value="Aham"
    )

    st.markdown("### 👥 Online Users")

    st.markdown("🟢 Alex")
    st.markdown("🟢 Rahul")
    st.markdown("🟢 Priya")
    st.markdown("⚪ Rohan")

    st.markdown("---")

    st.info(
        "ChatSpace\n\n"
        "A simple real-time chat application."
    )


# ---------- Main ----------
st.markdown(
    '<div class="title">💬 ChatSpace</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Connect and chat with your friends</div>',
    unsafe_allow_html=True
)

st.markdown("### 🟢 General Chat")

st.markdown('<div class="chat-box">', unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:

    if msg["user"] == username:

        st.markdown(
            f"""
            <div class="my-message">
                <div class="user-name">You</div>
                {msg["message"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="message">
                <div class="user-name">{msg["user"]}</div>
                {msg["message"]}
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)


# ---------- Message Input ----------
message = st.chat_input("Type a message...")

if message:

    if username.strip() == "":
        st.warning("Please enter your name first.")

    else:

        current_time = datetime.now().strftime("%H:%M")

        st.session_state.messages.append(
            {
                "user": username,
                "message": message,
                "time": current_time
            }
        )

        st.rerun()