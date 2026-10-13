import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import html
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="Aysuu Messenger",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

IST = ZoneInfo("Asia/Kolkata")
DB = Path(__file__).with_name("aysuu_chat.db")

AVATARS = {
    "Boy 1": "👨🏻",
    "Boy 2": "🧑🏻",
    "Boy 3": "👨🏽",
    "Girl 1": "👩🏻",
    "Girl 2": "👩🏼",
    "Girl 3": "👩🏽",
    "Cool": "😎",
    "Cat": "🐱",
    "Robot": "🤖",
    "Ghost": "👻",
}

def now_ist():
    return datetime.now(IST)

def time_text(value):
    try:
        return datetime.fromisoformat(value).astimezone(IST).strftime("%I:%M %p")
    except (ValueError, TypeError):
        return "--:--"


# ==========================================
# DATABASE
# ==========================================

def db_connect():
    conn = sqlite3.connect("chat_v2.db", timeout=20)
    conn.execute("PRAGMA busy_timeout = 20000")
    return conn


def init_db():
    with db_connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                user TEXT NOT NULL,
                avatar TEXT NOT NULL DEFAULT '😎',
                kind TEXT NOT NULL DEFAULT 'text',
                body TEXT,
                image BLOB,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS room_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                user TEXT NOT NULL,
                avatar TEXT NOT NULL,
                event TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()


def save_text(room, user, avatar, text):
    with db_connect() as conn:
        conn.execute("""
            INSERT INTO messages
            (room, user, avatar, kind, body, image, created_at)
            VALUES (?, ?, ?, 'text', ?, NULL, ?)
        """, (
            room, user, avatar, text,
            now_ist().isoformat()
        ))


def save_image(room, user, avatar, image_bytes, caption):
    with db_connect() as conn:
        conn.execute("""
            INSERT INTO messages
            (room, user, avatar, kind, body, image, created_at)
            VALUES (?, ?, ?, 'image', ?, ?, ?)
        """, (
            room, user, avatar, caption,
            sqlite3.Binary(image_bytes),
            now_ist().isoformat()
        ))


def load_messages(room):
    with db_connect() as conn:
        rows = conn.execute("""
            SELECT id, user, avatar, kind, body, image, created_at
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT 500
        """, (room,)).fetchall()

    return list(reversed(rows))


def add_room_event(room, user, avatar):
    with db_connect() as conn:
        conn.execute("""
            INSERT INTO room_events
            (room, user, avatar, event, created_at)
            VALUES (?, ?, ?, 'joined', ?)
        """, (
            room, user, avatar,
            now_ist().isoformat()
        ))


def load_events(room):
    with db_connect() as conn:
        return conn.execute("""
            SELECT id, user, avatar, created_at
            FROM room_events
            WHERE room = ?
            ORDER BY id DESC
            LIMIT 10
        """, (room,)).fetchall()


init_db()


# ==========================================
# SESSION
# ==========================================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "username" not in st.session_state:
    st.session_state.username = "Aham"

if "avatar" not in st.session_state:
    st.session_state.avatar = "😎"

if "room" not in st.session_state:
    st.session_state.room = "Friends"

if "joined_room" not in st.session_state:
    st.session_state.joined_room = None

if "notice" not in st.session_state:
    st.session_state.notice = ""
    if "show_call" not in st.session_state:
        st.session_state.show_call=False
        if "call_type" not in st.session_state:
            st.session_state.call_type+"video"


# ==========================================
# PREMIUM CSS
# ==========================================

st.markdown("""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

.stApp {
    background:
        radial-gradient(ellipse at 0% 0%, #1e1b4b 0%, transparent 38%),
        radial-gradient(ellipse at 100% 30%, #172554 0%, transparent 35%),
        linear-gradient(145deg, #060816, #0b1020 55%, #080b18);
    color: #f8fafc;
    font-family: Inter, sans-serif;
}

.block-container {
    max-width: 1150px;
    padding-top: 1.7rem;
    padding-bottom: 4rem;
}

.aysuu-header {
    padding: 26px;
    border-radius: 25px;
    background: linear-gradient(
        130deg,
        rgba(30,41,89,.88),
        rgba(17,24,39,.86)
    );
    border: 1px solid rgba(167,139,250,.25);
    box-shadow: 0 15px 55px rgba(0,0,0,.28);
    margin-bottom: 22px;
}

.logo {
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -1.2px;
}

.gradient {
    background: linear-gradient(90deg,#60a5fa,#c084fc,#f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.tagline {
    color: #a5b4fc;
    font-size: 11px;
    letter-spacing: 2px;
    margin-top: 7px;
}

.panel {
    padding: 19px;
    background: rgba(15,23,42,.72);
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 20px;
    margin-bottom: 16px;
}

.chat-message {
    display: flex;
    gap: 11px;
    align-items: flex-start;
    margin: 18px 0;
}

.avatar {
    min-width: 43px;
    height: 43px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    background: linear-gradient(135deg,#312e81,#1e293b);
    border: 1px solid rgba(167,139,250,.3);
    border-radius: 15px;
}

.bubble {
    padding: 12px 15px;
    max-width: 100%;
    background: #172036;
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 5px 17px 17px 17px;
    overflow-wrap: anywhere;
}

.my-bubble {
    background: linear-gradient(135deg,#4338ca,#6d28d9);
    border-radius: 17px 5px 17px 17px;
}

.username {
    color: #c4b5fd;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 5px;
}

.timestamp {
    font-size: 10px;
    color: #cbd5e1;
    margin-top: 7px;
}

.online-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
    margin-right: 7px;
}

div.stButton > button {
    min-height: 43px;
    border-radius: 13px;
    background: #171e35;
    color: white;
    border: 1px solid rgba(148,163,184,.2);
    font-weight: 600;
    transition: .2s;
}

div.stButton > button:hover {
    background: #312e81;
    border-color: #a78bfa;
    color: white;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
}

[data-testid="stFileUploader"] {
    background: rgba(30,41,59,.4);
    border-radius: 15px;
    padding: 8px;
}

hr {
    border-color: rgba(148,163,184,.15);
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR / PROFILE
# ==========================================

with st.sidebar:
    st.markdown("## ⚡ Aysuu")
    st.caption("YOUR PEOPLE. YOUR SPACE.")

    st.markdown("---")

    new_name = st.text_input(
        "Your display name",
        value=st.session_state.username,
        max_chars=30
    ).strip()

    avatar_choice = st.selectbox(
        "Choose your avatar",
        list(AVATARS.keys()),
        index=next(
            (i for i, key in enumerate(AVATARS)
             if AVATARS[key] == st.session_state.avatar),
            6
        )
    )

    new_avatar = AVATARS[avatar_choice]

    new_room = st.text_input(
        "Room name",
        value=st.session_state.room,
        max_chars=50
    ).strip()

    if not new_name:
        new_name = "Guest"

    if not new_room:
        new_room = "Friends"

    if (
        new_name != st.session_state.username
        or new_avatar != st.session_state.avatar
        or new_room != st.session_state.room
    ):
        st.session_state.username = new_name
        st.session_state.avatar = new_avatar
        st.session_state.room = new_room
        st.session_state.joined_room = None
        st.rerun()

    st.markdown("---")
    st.markdown("### Your profile")

    st.markdown(
        f"<div class='panel' style='text-align:center'>"
        f"<div style='font-size:48px'>{html.escape(st.session_state.avatar)}</div>"
        f"<div style='font-size:18px;font-weight:700'>"
        f"{html.escape(st.session_state.username)}</div>"
        f"<div style='color:#94a3b8;font-size:12px'>"
        f"Room: {html.escape(st.session_state.room)}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.caption("Messages and images are stored locally.")


# ==========================================
# JOIN ROOM EVENT
# ==========================================

if st.session_state.joined_room != st.session_state.room:
    add_room_event(
        st.session_state.room,
        st.session_state.username,
        st.session_state.avatar
    )

    st.session_state.joined_room = st.session_state.room
    st.session_state.notice = (
        f"{st.session_state.avatar} "
        f"{st.session_state.username} joined the room"
    )


# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div class="aysuu-header">
    <div class="logo">⚡ <span class="gradient">Aysuu Messenger</span></div>
    <div class="tagline">PRIVATE CHATS · GOOD VIBES · YOUR PEOPLE</div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([3, 2])

with left:
    st.markdown(f"### 💬 {html.escape(st.session_state.room)}")
    st.caption("Your personal conversation space")

with right:
    st.markdown(
        f"<div style='text-align:right;padding-top:15px'>"
        f"<span class='online-dot'></span>"
        f"<span style='color:#86efac'>IST · {now_ist().strftime('%I:%M %p')}</span>"
        f"</div>",
        unsafe_allow_html=True
    )


# ==========================================
# CALL BUTTONS
# ==========================================

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("📞 Audio Call", use_container_width=True, key="audio_call"):
        st.session_state.show_call = not st.session_state.show_call
        st.session_state.call_type = "audio"

with c2:
    if st.button("📹 Video Call", use_container_width=True, key="video_call"):
        st.session_state.show_call = not st.session_state.show_call
        st.session_state.call_type = "video"

with c3:
    st.button(
        "🎞️ GIF",
        use_container_width=True,
        disabled=True,
        key="gif_button"
    )

st.caption(
    "Calling and GIF search need additional real-time service integration."
)

st.markdown("---")


# ==========================================
# RECENT ROOM EVENTS
# ==========================================

with st.expander("👥 Recent room activity", expanded=False):
    events = load_events(st.session_state.room)

    if not events:
        st.caption("No room activity yet.")

    for event_id, event_user, event_avatar, event_time in events:
        st.write(
            f"{event_avatar} **{event_user}** joined · "
            f"{time_text(event_time)}"
        )

if st.session_state.notice:
    st.info(st.session_state.notice)


# ==========================================
# CHAT HISTORY
# ==========================================

st.markdown("### 💬 Messages")

messages = load_messages(st.session_state.room)

if not messages:
    st.markdown("""
    <div class="panel">
        <h3>👋 Start your conversation</h3>
        <p style="color:#94a3b8">
            Send a message or share a picture with your friends.
        </p>
    </div>
    """, unsafe_allow_html=True)

for (
    message_id,
    message_user,
    message_avatar,
    kind,
    body,
    image_bytes,
    created_at
) in messages:

    is_mine = message_user == st.session_state.username
    bubble_class = "bubble my-bubble" if is_mine else "bubble"

    safe_name = html.escape(
        "You" if is_mine else message_user
    )

    safe_body = html.escape(body or "")
    safe_time = time_text(created_at)

    st.markdown(
        f"""
        <div class="chat-message">
            <div class="avatar">{html.escape(message_avatar)}</div>
            <div class="{bubble_class}">
                <div class="username">{safe_name}</div>
                {safe_body.replace(chr(10), '<br>')}
                <div class="timestamp">{safe_time}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if kind == "image" and image_bytes:
        st.image(
            bytes(image_bytes),
            caption=f"{message_user} · {safe_time}",
            width=400
        )


# ==========================================
# IMAGE UPLOAD + PREVIEW
# ==========================================

st.markdown("---")
st.markdown("### 🖼️ Share a picture")

uploaded_image = st.file_uploader(
    "Choose an image",
    type=["png", "jpg", "jpeg", "webp"],
    key="image_upload"
)

image_caption = st.text_input(
    "Image caption (optional)",
    key="image_caption"
)

if uploaded_image:
    if uploaded_image.size > 5 * 1024 * 1024:
        st.error("Image must be 5 MB or smaller.")
        uploaded_image = None
    else:
        st.image(
            uploaded_image,
            caption="Preview",
            width=350
        )

if st.button(
    "📤 Send Image",
    use_container_width=True,
    key="send_image"
):
    if not uploaded_image:
        st.warning("Please select an image first.")
    elif uploaded_image.size > 5 * 1024 * 1024:
        st.error("Image is too large. Maximum size is 5 MB.")
    else:
        save_image(
            st.session_state.room,
            st.session_state.username,
            st.session_state.avatar,
            uploaded_image.getvalue(),
            image_caption.strip()
        )

        st.session_state.notice = "Image saved successfully!"
        st.rerun()


# ==========================================
# TEXT MESSAGE INPUT
# ==========================================

new_message = st.chat_input(
    "Write a message...",
    key="message_input"
)

if new_message and new_message.strip():
    save_text(
        st.session_state.room,
        st.session_state.username,
        st.session_state.avatar,
        new_message.strip()
    )

    st.rerun()


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#64748b;font-size:12px">
        ⚡ Aysuu Messenger<br>
        Made with Python & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
