import streamlit as st
import sqlite3
import html
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Aysuu Messenger",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

IST = ZoneInfo("Asia/Kolkata")
DB_PATH = Path(__file__).with_name("aysuu_chat.db")


def current_time():
    return datetime.now(IST).strftime("%I:%M %p")


def current_timestamp():
    return datetime.now(IST).isoformat(timespec="seconds")


# ==================================================
# DATABASE — LOCAL PERSISTENT STORAGE
# ==================================================

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                user TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def save_message(room, user, message):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO messages (room, user, message, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (room, user, message, current_timestamp())
        )
        conn.commit()


def load_messages(room, limit=500):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT user, message, created_at
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (room, limit)
        ).fetchall()

    return [
        {
            "user": row[0],
            "text": row[1],
            "time": row[2]
        }
        for row in reversed(rows)
    ]


init_db()


# ==================================================
# PREMIUM DESIGN
# ==================================================

st.markdown("""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

.stApp {
    background:
        radial-gradient(ellipse at top left, #172554 0%, transparent 40%),
        linear-gradient(135deg, #070b16, #101729 55%, #080c18);
    color: #f8fafc;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.aysuu-header {
    padding: 26px;
    border-radius: 24px;
    background: rgba(15, 23, 42, .8);
    border: 1px solid rgba(148, 163, 184, .18);
    margin-bottom: 22px;
}

.aysuu-logo {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
}

.aysuu-gradient {
    background: linear-gradient(90deg, #60a5fa, #c084fc, #f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.aysuu-subtitle {
    color: #94a3b8;
    margin-top: 7px;
    font-size: 12px;
    letter-spacing: 1.4px;
}

.aysuu-panel {
    padding: 18px;
    border: 1px solid rgba(148, 163, 184, .15);
    border-radius: 20px;
    background: rgba(15, 23, 42, .68);
    margin-bottom: 18px;
}

.aysuu-message {
    background: #1e293b;
    padding: 12px 16px;
    border-radius: 5px 18px 18px 18px;
    margin: 8px 0 15px;
    max-width: 82%;
    width: fit-content;
    overflow-wrap: anywhere;
    border: 1px solid rgba(148, 163, 184, .12);
}

.aysuu-own {
    background: linear-gradient(135deg, #2563eb, #6d28d9);
    padding: 12px 16px;
    border-radius: 18px 5px 18px 18px;
    margin: 8px 0 15px auto;
    max-width: 82%;
    width: fit-content;
    overflow-wrap: anywhere;
}

.aysuu-name {
    font-size: 12px;
    color: #c4b5fd;
    font-weight: 700;
    margin-bottom: 5px;
}

.aysuu-time {
    color: #cbd5e1;
    font-size: 10px;
    margin-top: 7px;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 42px;
    background: #172036;
    color: white;
    border: 1px solid rgba(148, 163, 184, .25);
    font-weight: 600;
}

div.stButton > button:hover {
    background: #293858;
    color: white;
    border-color: #818cf8;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
}

hr {
    border-color: rgba(148, 163, 184, .15);
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

if "username" not in st.session_state:
    st.session_state.username = "Aham"

if "room" not in st.session_state:
    st.session_state.room = "Friends"


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("## ⚡ Aysuu Messenger")
    st.caption("YOUR SPACE. YOUR PEOPLE.")

    st.markdown("---")

    st.session_state.username = st.text_input(
        "Your display name",
        value=st.session_state.username,
        max_chars=30
    ).strip() or "Guest"

    st.session_state.room = st.text_input(
        "Room name",
        value=st.session_state.room,
        max_chars=50
    ).strip() or "Friends"

    st.markdown("---")

    st.markdown("### 🟢 Your session")
    st.write(f"👤 {st.session_state.username}")
    st.write(f"💬 {st.session_state.room}")

    st.markdown("---")

    st.caption("Messages are stored in a local SQLite database.")

    st.warning(
        "This local version does not synchronize messages "
        "between different devices."
    )


# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="aysuu-header">
    <div class="aysuu-logo">
        ⚡ <span class="aysuu-gradient">Aysuu Messenger</span>
    </div>
    <div class="aysuu-subtitle">
        PRIVATE CONVERSATIONS · YOUR OWN SPACE
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# ROOM HEADER
# ==================================================

left, right = st.columns([3, 2])

with left:
    st.markdown(
        f"### 💬 {html.escape(st.session_state.room)}"
    )
    st.caption("Your conversation space")

with right:
    st.markdown(
        f"<div style='text-align:right;color:#86efac;padding-top:15px'>"
        f"🕒 India Standard Time · {current_time()}</div>",
        unsafe_allow_html=True
    )


# ==================================================
# CALL BUTTONS — PLACEHOLDERS
# ==================================================

call1, call2, call3 = st.columns(3)

with call1:
    st.button(
        "📞 Audio Call",
        key="audio_call",
        use_container_width=True,
        disabled=True
    )

with call2:
    st.button(
        "📹 Video Call",
        key="video_call",
        use_container_width=True,
        disabled=True
    )

with call3:
    st.button(
        "🎞️ GIF",
        key="gif_button",
        use_container_width=True,
        disabled=True
    )

st.caption(
    "Audio/video calls and GIF search require additional service integration."
)

st.markdown("---")


# ==================================================
# CHAT HISTORY
# ==================================================

messages = load_messages(st.session_state.room)

st.markdown("### 💬 Conversation")

if not messages:
    st.markdown("""
    <div class="aysuu-panel">
        <h3>👋 Welcome to Aysuu Messenger</h3>
        <p style="color:#94a3b8">
            Your conversation starts here. Send your first message below.
        </p>
    </div>
    """, unsafe_allow_html=True)

for msg in messages:
    own = msg["user"] == st.session_state.username

    bubble_class = "aysuu-own" if own else "aysuu-message"
    display_name = "You" if own else msg["user"]

    try:
        timestamp = datetime.fromisoformat(msg["time"])
        display_time = timestamp.astimezone(IST).strftime("%I:%M %p")
    except (ValueError, TypeError):
        display_time = "--:--"

    safe_name = html.escape(display_name)
    safe_text = html.escape(msg["text"]).replace("\n", "<br>")
    safe_time = html.escape(display_time)

    st.markdown(
        f"""
        <div class="{bubble_class}">
            <div class="aysuu-name">{safe_name}</div>
            <div>{safe_text}</div>
            <div class="aysuu-time">{safe_time}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==================================================
# MESSAGE COMPOSER
# ==================================================

new_message = st.chat_input(
    "Write a message...",
    key="message_composer"
)

if new_message and new_message.strip():
    save_message(
        st.session_state.room,
        st.session_state.username,
        new_message.strip()
    )
    st.rerun()


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;color:#64748b;font-size:12px">
        ⚡ Aysuu Messenger<br>
        Built with Python & Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
