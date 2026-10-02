import streamlit as st
from datetime import datetime
import html
import hashlib
import secrets

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="ChatSpace // Private",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CYBERPUNK CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background: radial-gradient(
        circle at 15% 15%,
        #0d1224 0%,
        #05070f 100%
    );
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background: rgba(10, 15, 30, 0.85);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

.msg-card {
    padding: 14px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
    max-width: 80%;
    line-height: 1.5;
    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}

.msg-mine {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.msg-theirs {
    background: rgba(22,28,48,0.9);
    border: 1px solid rgba(255,255,255,0.07);
    color: #f1f5f9;
    margin-right: auto;
    border-bottom-left-radius: 4px;
}

.msg-header {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    opacity: 0.8;
}

.msg-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    opacity: 0.6;
}

.room-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 999px;
    background: rgba(99,102,241,0.15);
    border: 1px solid #6366f1;
    color: #818cf8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
}

.lock-box {
    padding: 18px;
    border-radius: 18px;
    background: rgba(22,28,48,0.65);
    border: 1px solid rgba(99,102,241,0.3);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# =========================
# GLOBAL CHAT STORAGE
# =========================
@st.cache_resource
def get_global_store():
    return {}

chat_rooms = get_global_store()


# =========================
# SESSION STATE
# =========================
if "connected_room" not in st.session_state:
    st.session_state.connected_room = None

if "verified" not in st.session_state:
    st.session_state.verified = False


# =========================
# HASH ROOM KEY
# =========================
def hash_room_key(room_key):
    return hashlib.sha256(
        room_key.encode("utf-8")
    ).hexdigest()


# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.markdown("### 🔐 **ChatSpace**")
    st.caption("Private Room • No Phone • No Email")
    st.divider()

    username = st.text_input(
        "👤 Your Alias",
        placeholder="e.g. Shadow",
        max_chars=18
    )

    room_key = st.text_input(
        "🔑 Private Room Key",
        placeholder="Enter secret key",
        type="password"
    )

    st.divider()

    connect = st.button(
        "🔓 Enter Private Room",
        use_container_width=True
    )

    leave = st.button(
        "🚪 Leave Room",
        use_container_width=True
    )

    if leave:
        st.session_state.connected_room = None
        st.session_state.verified = False
        st.rerun()


# =========================
# CONNECT TO ROOM
# =========================
if connect:

    if not username.strip():
        st.error("Please enter your alias.")

    elif not room_key.strip():
        st.error("Please enter the private room key.")

    else:
        room_hash = hash_room_key(room_key.strip())

        # Create room
        if room_hash not in chat_rooms:
            chat_rooms[room_hash] = {
                "messages": [],
                "users": set(),
                "created": datetime.now().strftime("%d-%m-%Y %I:%M %p")
            }

        st.session_state.connected_room = room_hash
        st.session_state.verified = True

        chat_rooms[room_hash]["users"].add(
            username.strip()
        )

        st.rerun()


# =========================
# MAIN PAGE
# =========================
if not st.session_state.verified:

    st.markdown("""
    <div class="lock-box" style="margin-top:120px;">
        <h1>🔐 Private ChatSpace</h1>

        <p style="color:#94a3b8;">
            Enter your alias and secret room key
            to join a private room.
        </p>

        <p style="color:#818cf8;">
            Only people with the same room key
            can access that room.
        </p>
    </div>
    """, unsafe_allow_html=True)

else:

    room_hash = st.session_state.connected_room
    room = chat_rooms[room_hash]

    # Keep current user registered
    room["users"].add(username.strip())

    # =========================
    # HEADER
    # =========================
    st.markdown(
        """
        <div>
            <span class="room-badge">
                🔒 PRIVATE ROOM
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 💬 Secure Chat")

    col1, col2 = st.columns([8, 2])

    with col1:
        st.caption(
            "Your messages are visible only inside this room."
        )

    with col2:
        st.metric(
            "Participants",
            len(room["users"])
        )

    st.divider()


    # =========================
    # CHAT DISPLAY
    # =========================
    if not room["messages"]:

        st.info(
            "This private room is empty. Send the first message! 👋"
        )

    else:

        for msg in room["messages"]:

            is_me = (
                msg["user"] == username.strip()
            )

            bubble_class = (
                "msg-mine"
                if is_me
                else "msg-theirs"
            )

            tag = (
                "You"
                if is_me
                else html.escape(msg["user"])
            )

            safe_content = html.escape(
                msg["content"]
            )

            safe_time = html.escape(
                msg["time"]
            )

            st.markdown(
                f"""
                <div class="msg-card {bubble_class}">

                    <div class="msg-header">
                        <span>{tag}</span>
                        <span class="msg-time">
                            {safe_time}
                        </span>
                    </div>

                    <div>
                        {safe_content}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    # =========================
    # SEND MESSAGE
    # =========================
    with st.form(
        "chat_input_form",
        clear_on_submit=True
    ):

        user_msg = st.text_input(
            "Message",
            placeholder="Type your private message...",
            label_visibility="collapsed",
            max_chars=1000
        )

        send_btn = st.form_submit_button(
            "Send 🚀",
            use_container_width=True
        )

        if send_btn and user_msg.strip():

            room["messages"].append({

                "user": username.strip(),

                "content": user_msg.strip(),

                "time": datetime.now().strftime(
                    "%I:%M %p"
                )
            })

            st.rerun()


    # =========================
    # ROOM CONTROLS
    # =========================
    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑️ Clear This Room",
            use_container_width=True
        ):

            room["messages"] = []
            st.rerun()

    with col2:

        if st.button(
            "🚪 Leave Private Room",
            use_container_width=True
        ):

            st.session_state.connected_room = None
            st.session_state.verified = False
            st.rerun()


# =========================
# FOOTER
# =========================
st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748b;
        margin-top:40px;
        font-size:12px;
    ">
        🔐 ChatSpace Private Room
        • Share your room key only with trusted people
    </div>
    """,
    unsafe_allow_html=True
)
