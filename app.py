import streamlit as st
from datetime import datetime
import hashlib
import html
import base64

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="ChatSpace Ultra",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 20%, #111827 0%, #020617 65%);
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.96) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.stButton > button {
    border-radius: 12px;
    font-weight: 600;
}

.private-card {
    padding: 35px;
    margin-top: 100px;
    border-radius: 22px;
    text-align: center;
    background: rgba(15,23,42,0.75);
    border: 1px solid rgba(129,140,248,0.25);
}

.room-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(129,140,248,0.5);
    color: #a5b4fc;
    font-size: 13px;
}

.chat-message {
    padding: 13px 16px;
    border-radius: 17px;
    margin-bottom: 10px;
    background: rgba(30,41,59,0.80);
    border: 1px solid rgba(255,255,255,0.06);
}

.chat-message.mine {
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
}

.user-name {
    font-size: 12px;
    font-weight: 700;
}

.message-time {
    font-size: 10px;
    opacity: 0.55;
}

.message-text {
    margin-top: 5px;
    word-wrap: break-word;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# GLOBAL MEMORY
# =========================================================

@st.cache_resource
def get_chat_store():
    return {}


chat_rooms = get_chat_store()


# =========================================================
# ROOM KEY HASH
# =========================================================

def make_room_id(room_key):
    return hashlib.sha256(
        room_key.strip().encode("utf-8")
    ).hexdigest()


# =========================================================
# STICKERS / GIFS
# =========================================================

STICKERS = [
    (
        "🔥 Fire",
        "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
    ),
    (
        "😂 Laugh",
        "https://media.giphy.com/media/26n6Gx9moCgs1DflG/giphy.gif"
    ),
    (
        "❤️ Love",
        "https://media.giphy.com/media/R6gVNROjBy4UM/giphy.gif"
    ),
    (
        "😎 Cool",
        "https://media.giphy.com/media/jpbnoe3UIa8TU8LM13/giphy.gif"
    ),
    (
        "🎉 Party",
        "https://media.giphy.com/media/blSTtZehjAZ8I/giphy.gif"
    ),
    (
        "👀 Shock",
        "https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif"
    ),
    (
        "🚀 Rocket",
        "https://media.giphy.com/media/3ohnEqJ1XOfvWaSk7e/giphy.gif"
    ),
    (
        "👋 Bye",
        "https://media.giphy.com/media/ASd0Ukj0BC5roG5Lmp/giphy.gif"
    )
]


# =========================================================
# SESSION STATE
# =========================================================

if "connected_room" not in st.session_state:
    st.session_state.connected_room = None

if "current_user" not in st.session_state:
    st.session_state.current_user = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("### 🔐 ChatSpace Ultra")

    st.caption(
        "Private Rooms • Anonymous • No SQL"
    )

    st.divider()

    username = st.text_input(
        "👤 Your Alias",
        placeholder="e.g. Shadow",
        max_chars=18
    )

    room_key = st.text_input(
        "🔑 Private Room Key",
        placeholder="Minimum 6 characters",
        type="password"
    )

    st.divider()

    connect_button = st.button(
        "🔓 Enter Private Room",
        use_container_width=True
    )

    if connect_button:

        clean_name = username.strip()
        clean_key = room_key.strip()

        if not clean_name:

            st.error("Enter your alias.")

        elif len(clean_key) < 6:

            st.error(
                "Room Key must contain at least 6 characters."
            )

        else:

            # Room ID is a hash.
            # The original room key is not stored.
            room_id = make_room_id(clean_key)

            if room_id not in chat_rooms:

                chat_rooms[room_id] = {
                    "messages": [],
                    "users": set()
                }

            chat_rooms[room_id]["users"].add(
                clean_name
            )

            st.session_state.connected_room = room_id
            st.session_state.current_user = clean_name

            st.rerun()

    # -----------------------------------------------------
    # CONNECTED CONTROLS
    # -----------------------------------------------------

    if st.session_state.connected_room:

        room_id = st.session_state.connected_room

        st.divider()

        if room_id in chat_rooms:

            active_users = len(
                chat_rooms[room_id]["users"]
            )

            st.metric(
                "👥 Participants",
                max(active_users, 1)
            )

            st.metric(
                "💬 Messages",
                len(
                    chat_rooms[room_id]["messages"]
                )
            )

        st.divider()

        if st.button(
            "🗑️ Clear Room",
            use_container_width=True
        ):

            if room_id in chat_rooms:

                chat_rooms[room_id]["messages"] = []

            st.rerun()

        if st.button(
            "🚪 Leave Room",
            use_container_width=True
        ):

            st.session_state.connected_room = None
            st.session_state.current_user = None

            st.rerun()


# =========================================================
# NOT CONNECTED SCREEN
# =========================================================

if not st.session_state.connected_room:

    st.markdown("""
    <div class="private-card">

        <h1>🔐 ChatSpace Ultra</h1>

        <p style="color:#94a3b8;">
            Your private room for anonymous chatting.
        </p>

        <p style="color:#818cf8;">
            Share your Room Key only with the people
            you want inside the room.
        </p>

        <p style="color:#64748b;">
            No phone number • No email • No SQL
        </p>

    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# CONNECTED ROOM
# =========================================================

room_id = st.session_state.connected_room
current_user = st.session_state.current_user

room = chat_rooms[room_id]

# Make sure current user remains registered.
room["users"].add(current_user)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<span class="room-badge">🔒 PRIVATE ROOM</span>',
    unsafe_allow_html=True
)

st.title("💬 ChatSpace")

col1, col2 = st.columns([7, 2])

with col1:

    st.caption(
        f"Connected as **{current_user}**"
    )

with col2:

    st.metric(
        "👥 Active",
        len(room["users"])
    )

st.divider()


# =========================================================
# DISPLAY CHAT
# =========================================================

if not room["messages"]:

    st.info(
        "💬 No messages yet. Start the conversation!"
    )

else:

    for message in room["messages"]:

        is_me = (
            message["user"] == current_user
        )

        safe_user = html.escape(
            message["user"]
        )

        safe_content = html.escape(
            message["content"]
        )

        safe_time = html.escape(
            message["time"]
        )

        css_class = (
            "chat-message mine"
            if is_me
            else "chat-message"
        )

        # ---------------- TEXT ----------------

        if message["type"] == "text":

            st.markdown(
                f"""
                <div class="{css_class}">

                    <div class="user-name">
                        {safe_user}

                        <span class="message-time">
                            • {safe_time}
                        </span>
                    </div>

                    <div class="message-text">
                        {safe_content}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------- GIF ----------------

        elif message["type"] == "gif":

            st.markdown(
                f"""
                <div class="{css_class}">

                    <div class="user-name">
                        {safe_user}

                        <span class="message-time">
                            • {safe_time}
                        </span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.image(
                message["content"],
                width=220
            )

        # ---------------- IMAGE ----------------

        elif message["type"] == "image":

            st.markdown(
                f"""
                <div class="{css_class}">

                    <div class="user-name">
                        {safe_user}

                        <span class="message-time">
                            • {safe_time}
                        </span>
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            try:

                image_bytes = base64.b64decode(
                    message["content"]
                )

                st.image(
                    image_bytes,
                    width=400
                )

            except Exception:

                st.warning(
                    "Unable to display this image."
                )


# =========================================================
# MEDIA AREA
# =========================================================

with st.expander(
    "✨ Photo • Sticker • GIF"
):

    tab_photo, tab_sticker = st.tabs(
        [
            "📷 Photo",
            "🎭 Stickers"
        ]
    )

    # =====================================================
    # PHOTO
    # =====================================================

    with tab_photo:

        uploaded_file = st.file_uploader(
            "Choose a photo",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="photo_upload"
        )

        if uploaded_file is not None:

            if st.button(
                "🚀 Send Photo",
                use_container_width=True
            ):

                image_bytes = uploaded_file.read()

                # Store image as Base64 inside memory.
                image_base64 = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                room["messages"].append({

                    "user": current_user,

                    "type": "image",

                    "content": image_base64,

                    "time": datetime.now().strftime(
                        "%I:%M %p"
                    )
                })

                st.rerun()

    # =====================================================
    # STICKERS
    # =====================================================

    with tab_sticker:

        sticker_columns = st.columns(4)

        for index, (name, url) in enumerate(STICKERS):

            with sticker_columns[index % 4]:

                st.image(
                    url,
                    width=70
                )

                if st.button(
                    name,
                    key=f"sticker_{index}",
                    use_container_width=True
                ):

                    room["messages"].append({

                        "user": current_user,

                        "type": "gif",

                        "content": url,

                        "time": datetime.now().strftime(
                            "%I:%M %p"
                        )
                    })

                    st.rerun()


# =========================================================
# TEXT MESSAGE
# =========================================================

with st.form(
    "message_form",
    clear_on_submit=True
):

    chat_text = st.text_input(
        "Message",
        placeholder="Type your private message...",
        label_visibility="collapsed",
        max_chars=2000
    )

    send_button = st.form_submit_button(
        "🚀 Send",
        use_container_width=True
    )

    if send_button and chat_text.strip():

        room["messages"].append({

            "user": current_user,

            "type": "text",

            "content": chat_text.strip(),

            "time": datetime.now().strftime(
                "%I:%M %p"
            )
        })

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🔐 ChatSpace Ultra • Private Room • "
    "No SQL • Room key protected"
)
