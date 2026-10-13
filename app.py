import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import html
import uuid
import urllib.parse
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
        conn.commit()

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
        conn.commit()

def save_gif(room, user, avatar, gif_url):
    with db_connect() as conn:
        conn.execute("""
            INSERT INTO messages
            (room, user, avatar, kind, body, image, created_at)
            VALUES (?, ?, ?, 'gif', ?, NULL, ?)
        """, (
            room, user, avatar, gif_url,
            now_ist().isoformat()
        ))
        conn.commit()

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
        conn.commit()

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
    st.session_state.show_call = False

if "call_type" not in st.session_state:
    st.session_state.call_type = "video"

if "show_gif" not in st.session_state:
    st.session_state.show_gif = False

if "show_photo" not in st.session_state:
    st.session_state.show_photo = False

# ==========================================
# PREMIUM CSS
# ==========================================

st.markdown("""
<style>  
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');  
  
.stApp {  
    background:  
        radial-gradient(ellipse at 0% 0%, #1e1b4b 0%, transparent 40%),  
        radial-gradient(ellipse at 100% 30%, #0f172a 0%, #090d16 100%);  
    font-family: 'Inter', sans-serif;
    color: #f1f5f9;
}

.chat-bubble-me {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: #ffffff !important;
    padding: 10px 14px;
    border-radius: 14px 14px 2px 14px;
    margin-bottom: 6px;
    display: inline-block;
    max-width: 80%;
    word-break: break-word;
}

.chat-bubble-other {
    background: #1e293b;
    color: #f1f5f9 !important;
    padding: 10px 14px;
    border-radius: 14px 14px 14px 2px;
    margin-bottom: 6px;
    display: inline-block;
    max-width: 80%;
    word-break: break-word;
    border: 1px solid #334155;
}

.chat-time {
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 3px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.title("⚡ Aysuu")
    st.caption("YOUR PEOPLE. YOUR SPACE.")

    new_user = st.text_input("Your display name", value=st.session_state.username)
    if new_user:
        st.session_state.username = new_user

    avatar_choice = st.selectbox(
        "Choose your avatar",
        options=list(AVATARS.keys()),
        index=list(AVATARS.keys()).index("Cool") if "Cool" in AVATARS else 0
    )
    st.session_state.avatar = AVATARS[avatar_choice]

    new_room = st.text_input("Room name", value=st.session_state.room)
    if new_room:
        st.session_state.room = new_room

    st.markdown("---")
    st.markdown(f"**Your profile:** {st.session_state.avatar} `{st.session_state.username}`")
    st.markdown(f"**Current Room:** `{st.session_state.room}`")
    st.caption("Messages and images are stored locally.")

# Track Join Room
if st.session_state.joined_room != st.session_state.room:
    add_room_event(st.session_state.room, st.session_state.username, st.session_state.avatar)
    st.session_state.joined_room = st.session_state.room

# ==========================================
# MAIN INTERFACE
# ==========================================

st.subheader(f"💬 {st.session_state.room}")
st.caption("Your personal conversation space")

# Action Buttons
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("📞 Audio Call", use_container_width=True, key="btn_audio"):
        st.session_state.show_call = True
        st.session_state.call_type = "audio"
        st.session_state.show_gif = False
        st.session_state.show_photo = False

with c2:
    if st.button("📹 Video Call", use_container_width=True, key="btn_video"):
        st.session_state.show_call = True
        st.session_state.call_type = "video"
        st.session_state.show_gif = False
        st.session_state.show_photo = False

with c3:
    if st.button("🎭 GIF", use_container_width=True, key="btn_gif"):
        st.session_state.show_gif = not st.session_state.get("show_gif", False)
        st.session_state.show_call = False
        st.session_state.show_photo = False

with c4:
    if st.button("📷 Photo", use_container_width=True, key="btn_photo"):
        st.session_state.show_photo = not st.session_state.get("show_photo", False)
        st.session_state.show_call = False
        st.session_state.show_gif = False

# Live Call View
if st.session_state.get("show_call", False):
    safe_room = "".join(e for e in st.session_state.room if e.isalnum())
    is_audio = st.session_state.get("call_type") == "audio"
    call_url = f"https://meet.jit.si/aysuu_{safe_room}#config.startWithVideoMuted={'true' if is_audio else 'false'}"

    st.info(f"Connected to live room: {st.session_state.room}")
    components.iframe(call_url, height=500, scrolling=False)
    
    if st.button("❌ End Call", key="btn_end_call"):
        st.session_state.show_call = False
        st.rerun()

# GIF Sender
if st.session_state.get("show_gif", False):
    with st.expander("🎭 Send a GIF", expanded=True):
        gif_input = st.text_input("Direct GIF link paste karo (.gif URL):", placeholder="https://media.giphy.com/media/.../giphy.gif")
        if st.button("Send GIF 🚀", key="btn_submit_gif"):
            if gif_input.strip():
                save_gif(st.session_state.room, st.session_state.username, st.session_state.avatar, gif_input.strip())
                st.session_state.show_gif = False
                st.rerun()
            else:
                st.warning("Please enter a valid GIF URL")

# Photo Sender
if st.session_state.get("show_photo", False):
    with st.expander("📷 Upload & Send Photo", expanded=True):
        up_img = st.file_uploader("Select an Image", type=["jpg", "jpeg", "png"])
        caption = st.text_input("Caption (optional):")
        if up_img is not None:
            st.image(up_img, width=200, caption="Preview")
            if st.button("Send Photo 📤", key="btn_submit_photo"):
                save_image(st.session_state.room, st.session_state.username, st.session_state.avatar, up_img.read(), caption)
                st.session_state.show_photo = False
                st.rerun()

# Room Activity Expander
events = load_events(st.session_state.room)
with st.expander("👥 Recent room activity", expanded=False):
    for ev in events:
        st.caption(f"{ev[2]} **{ev[1]}** joined at {time_text(ev[3])}")

st.markdown("---")
st.subheader("Messages")

# Display Messages
messages = load_messages(st.session_state.room)
msg_container = st.container()

with msg_container:
    for msg in messages:
        # msg: (id, user, avatar, kind, body, image, created_at)
        is_me = (msg[1] == st.session_state.username)
        align = "right" if is_me else "left"
        bubble_cls = "chat-bubble-me" if is_me else "chat-bubble-other"

        st.markdown(
            f"<div style='text-align: {align}; margin-bottom: 8px;'>"
            f"<span style='font-size: 0.82rem; color: #94a3b8;'>{msg[2]} <b>{html.escape(msg[1])}</b></span><br>"
            f"<div class='{bubble_cls}'>",
            unsafe_allow_html=True
        )

        if msg[3] == "text":
            st.markdown(f"<span>{html.escape(msg[4] or '')}</span>", unsafe_allow_html=True)
        elif msg[3] == "gif":
            st.image(msg[4], width=260)
        elif msg[3] == "image" and msg[5]:
            st.image(msg[5], width=260)
            if msg[4]:
                st.caption(msg[4])

        st.markdown(
            f"<div class='chat-time'>{time_text(msg[6])}</div></div></div>",
            unsafe_allow_html=True
        )

# Chat Input Bar
user_input = st.chat_input("Write a message...")
if user_input:
    save_text(st.session_state.room, st.session_state.username, st.session_state.avatar, user_input)
    st.rerun()
