import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import html
import uuid
import requests
import time

from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from streamlit_autorefresh import st_autorefresh


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

DB_PATH = Path(__file__).parent / "chat_v2.db"

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
        return datetime.fromisoformat(value).astimezone(
            IST
        ).strftime("%I:%M %p")
    except (ValueError, TypeError):
        return "--:--"


# ==========================================
# DATABASE
# ==========================================

def db_connect():
    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=20
    )
    conn.execute("PRAGMA busy_timeout=20000")
    return conn


def init_db():
    with db_connect() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                user TEXT NOT NULL,
                avatar TEXT NOT NULL,
                kind TEXT NOT NULL,
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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS presence (
                session_id TEXT PRIMARY KEY,
                room TEXT NOT NULL,
                username TEXT NOT NULL,
                avatar TEXT NOT NULL,
                last_seen REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_room
            ON messages(room, id)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_presence_room
            ON presence(room, last_seen)
        """)


init_db()


# ==========================================
# MESSAGE FUNCTIONS
# ==========================================

def save_message(room, user, avatar, kind, body=None, image=None):

    with db_connect() as conn:

        conn.execute("""
            INSERT INTO messages
            (room, user, avatar, kind, body, image, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            room,
            user,
            avatar,
            kind,
            body,
            sqlite3.Binary(image) if image else None,
            now_ist().isoformat()
        ))


def load_messages(room):

    with db_connect() as conn:

        rows = conn.execute("""
            SELECT id, user, avatar, kind,
                   body, image, created_at
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT 500
        """, (room,)).fetchall()

    return list(reversed(rows))


# ==========================================
# ONLINE PRESENCE
# ==========================================

def update_presence(session_id, room, username, avatar):

    with db_connect() as conn:

        conn.execute("""
            INSERT INTO presence
            (session_id, room, username, avatar, last_seen)
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(session_id) DO UPDATE SET
                room = excluded.room,
                username = excluded.username,
                avatar = excluded.avatar,
                last_seen = excluded.last_seen
        """, (
            session_id,
            room,
            username,
            avatar,
            time.time()
        ))

        # Purane inactive sessions hatao
        conn.execute("""
            DELETE FROM presence
            WHERE last_seen < ?
        """, (time.time() - 60,))


def load_online_users(room):

    with db_connect() as conn:

        return conn.execute("""
            SELECT username, avatar, last_seen
            FROM presence
            WHERE room = ?
              AND last_seen > ?
            ORDER BY username
        """, (
            room,
            time.time() - 20
        )).fetchall()


def add_room_event(room, username, avatar):

    with db_connect() as conn:

        conn.execute("""
            INSERT INTO room_events
            (room, user, avatar, event, created_at)
            VALUES (?, ?, ?, 'joined', ?)
        """, (
            room,
            username,
            avatar,
            now_ist().isoformat()
        ))


def load_events(room):

    with db_connect() as conn:

        return conn.execute("""
            SELECT user, avatar, created_at
            FROM room_events
            WHERE room = ?
            ORDER BY id DESC
            LIMIT 10
        """, (room,)).fetchall()


# ==========================================
# SESSION
# ==========================================

defaults = {
    "session_id": str(uuid.uuid4()),
    "username": "Aham",
    "avatar": "😎",
    "room": "Friends",
    "joined_room": None,
    "show_call": False,
    "call_type": "video",
    "show_gif": False,
    "show_photo": False,
    "gif_query": "trending",
    "gif_results": [],
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# AUTO UPDATE
# ==========================================

# Messages and presence refresh automatically.
# No manual sync button required.

st_autorefresh(
    interval=5000,
    key="aysuu_live_refresh"
)


# ==========================================
# PREMIUM DESIGN
# ==========================================

st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

.stApp {
    background:
        radial-gradient(
            ellipse at 0% 0%,
            #312e81 0%,
            transparent 38%
        ),
        linear-gradient(
            135deg,
            #020617,
            #0f172a,
            #111827
        );

    color: #f1f5f9;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, p, label {
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

section[data-testid="stSidebar"] {
    background: #0b1120;
    border-right: 1px solid #273449;
}

div[data-testid="stChatMessage"] {
    background: rgba(30, 41, 59, 0.72);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 12px;
    margin-bottom: 12px;
}

div.stButton > button {
    border-radius: 12px;
    font-weight: 600;
    min-height: 42px;
    border: 1px solid #334155;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    border-color: #818cf8;
    color: #c7d2fe;
}

.chat-meta {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 5px;
}

.online-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 10px 12px;
    margin: 6px 0;
}

.online-dot {
    color: #4ade80;
}

.offline-dot {
    color: #64748b;
}

.app-brand {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
}

.app-subtitle {
    color: #94a3b8;
    font-size: 12px;
    letter-spacing: 2px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR / PROFILE
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="app-brand">⚡ Aysuu</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="app-subtitle">YOUR PEOPLE. YOUR SPACE.</div>',
        unsafe_allow_html=True
    )

    st.write("")

    st.subheader("Your Profile")

    username = st.text_input(
        "Display name",
        value=st.session_state.username,
        max_chars=30
    ).strip()

    if username:
        st.session_state.username = username

    avatar_names = list(AVATARS.keys())

    current_avatar = next(
        (
            name for name, emoji in AVATARS.items()
            if emoji == st.session_state.avatar
        ),
        "Cool"
    )

    avatar_choice = st.selectbox(
        "Choose avatar",
        avatar_names,
        index=avatar_names.index(current_avatar)
    )

    st.session_state.avatar = AVATARS[avatar_choice]

    st.divider()

    new_room = st.text_input(
        "Room name",
        value=st.session_state.room,
        max_chars=60
    ).strip()

    if new_room:
        st.session_state.room = new_room

    st.info(
        "Share the exact same room name with your friend."
    )

    st.divider()

    st.markdown("**Your current profile**")

    st.markdown(
        f"{st.session_state.avatar} "
        f"**{html.escape(st.session_state.username)}**"
    )

    st.caption(
        f"Room: {st.session_state.room}"
    )


# ==========================================
# ROOM ENTRY
# ==========================================

room = st.session_state.room
username = st.session_state.username
avatar = st.session_state.avatar

if st.session_state.joined_room != room:

    add_room_event(room, username, avatar)

    st.session_state.joined_room = room


update_presence(
    st.session_state.session_id,
    room,
    username,
    avatar
)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    f"## 💬 {html.escape(room)}"
)

st.caption(
    "A little space for your favourite people."
)


# ==========================================
# ONLINE MEMBERS
# ==========================================

online_users = load_online_users(room)

with st.expander(
    f"🟢 Members in this room ({len(online_users)} online)",
    expanded=True
):

    if online_users:

        for member_name, member_avatar, last_seen in online_users:

            safe_name = html.escape(member_name)

            st.markdown(
                f"""
                <div class="online-card">
                    <span class="online-dot">●</span>
                    {member_avatar}
                    <b>{safe_name}</b>
                    <span style="color:#4ade80;font-size:12px;">
                        &nbsp; Online
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.caption(
            "Abhi koi active member nahi mila."
        )


# ==========================================
# RECENT ROOM ACTIVITY
# ==========================================

with st.expander("👥 Recent room activity"):

    events = load_events(room)

    if not events:

        st.caption("No recent activity.")

    for event_user, event_avatar, created_at in events:

        st.write(
            f"{event_avatar} **{event_user}** joined "
            f"at {time_text(created_at)}"
        )


# ==========================================
# ACTION BUTTONS
# ==========================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    if st.button(
        "📞 Audio Call",
        use_container_width=True
    ):

        st.session_state.show_call = True
        st.session_state.call_type = "audio"
        st.session_state.show_gif = False
        st.session_state.show_photo = False


with c2:

    if st.button(
        "📹 Video Call",
        use_container_width=True
    ):

        st.session_state.show_call = True
        st.session_state.call_type = "video"
        st.session_state.show_gif = False
        st.session_state.show_photo = False


with c3:

    if st.button(
        "🎭 GIF Gallery",
        use_container_width=True
    ):

        st.session_state.show_gif = (
            not st.session_state.show_gif
        )

        st.session_state.show_call = False
        st.session_state.show_photo = False


with c4:

    if st.button(
        "📷 Photo",
        use_container_width=True
    ):

        st.session_state.show_photo = (
            not st.session_state.show_photo
        )

        st.session_state.show_call = False
        st.session_state.show_gif = False


# ==========================================
# AUDIO / VIDEO CALL
# ==========================================

if st.session_state.show_call:

    safe_room = "".join(
        ch for ch in room if ch.isalnum()
    )[:50] or "friends"

    is_audio = st.session_state.call_type == "audio"

    call_url = (
        f"https://meet.jit.si/aysuu_{safe_room}"
        f"#config.startWithVideoMuted="
        f"{'true' if is_audio else 'false'}"
    )

    st.info(
        "Call open hai. Apne friend ko bhi same room "
        "name aur call link share karna hoga."
    )

    components.iframe(
        call_url,
        height=500,
        scrolling=False
    )

    if st.button("❌ End Call"):

        st.session_state.show_call = False
        st.rerun()


# ==========================================
# GIF GALLERY
# ==========================================

if st.session_state.show_gif:

    st.markdown("### 🎭 Find your GIF")

    st.caption(
        "Search karo, GIF choose karo aur seedha chat mein bhejo."
    )

    try:
        tenor_key = st.secrets.get(
            "TENOR_API_KEY",
            ""
        )
    except Exception:
        tenor_key = ""

    if not tenor_key:

        st.warning(
            "GIF gallery activate karne ke liye Tenor API key "
            "configure karni hogi. Setup neeche diya hai."
        )

    else:

        with st.form("gif_search_form"):

            gif_query = st.text_input(
                "Search GIF",
                value=st.session_state.gif_query,
                placeholder="Funny, happy, hello..."
            )

            search_clicked = st.form_submit_button(
                "🔍 Search GIFs"
            )

        if search_clicked:

            st.session_state.gif_query = (
                gif_query.strip() or "trending"
            )

            try:

                response = requests.get(
                    "https://tenor.googleapis.com/v2/search",
                    params={
                        "q": st.session_state.gif_query,
                        "key": tenor_key,
                        "limit": 12,
                        "media_filter": "gif"
                    },
                    timeout=15
                )

                response.raise_for_status()

                st.session_state.gif_results = (
                    response.json().get("results", [])
                )

            except requests.RequestException:

                st.error(
                    "GIFs load nahi ho paayi. "
                    "Internet ya API key check karo."
                )

        if not st.session_state.gif_results:

            if not search_clicked:

                st.info(
                    "GIF search karne ke liye upar query likho."
                )

        results = st.session_state.gif_results

        for i in range(0, len(results), 2):

            cols = st.columns(2)

            for j, col in enumerate(cols):

                index = i + j

                if index >= len(results):
                    break

                item = results[index]

                media = item.get(
                    "media_formats", {}
                )

                gif_data = media.get("gif", {})

                gif_url = gif_data.get("url")

                if not gif_url:
                    continue

                with col:

                    st.image(
                        gif_url,
                        use_container_width=True
                    )

                    if st.button(
                        "📤 Send GIF",
                        key=f"send_gif_{index}",
                        use_container_width=True
                    ):

                        save_message(
                            room,
                            username,
                            avatar,
                            "gif",
                            gif_url
                        )

                        st.session_state.show_gif = False
                        st.rerun()


# ==========================================
# PHOTO UPLOAD
# ==========================================

if st.session_state.show_photo:

    st.markdown("### 📷 Send a Photo")

    uploaded_image = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png", "webp"],
        key="photo_upload"
    )

    caption = st.text_input(
        "Photo caption (optional)",
        key="photo_caption"
    )

    if uploaded_image:

        st.image(
            uploaded_image,
            width=240
        )

        if st.button("📤 Send Photo"):

            image_bytes = uploaded_image.getvalue()

            if len(image_bytes) > 5 * 1024 * 1024:

                st.error(
                    "Photo 5 MB se chhoti honi chahiye."
                )

            else:

                save_message(
                    room,
                    username,
                    avatar,
                    "image",
                    caption,
                    image_bytes
                )

                st.session_state.show_photo = False
                st.rerun()


# ==========================================
# CHAT HISTORY
# ==========================================

st.divider()

st.markdown("### 💬 Messages")

messages = load_messages(room)

if not messages:

    st.info(
        "Abhi koi message nahi hai. "
        "Pehla message bhejo! 👋"
    )

for msg in messages:

    (
        msg_id,
        msg_user,
        msg_avatar,
        msg_kind,
        msg_body,
        msg_image,
        msg_created
    ) = msg

    is_me = (
        msg_user == st.session_state.username
    )

    with st.chat_message(
        "user" if is_me else "assistant",
        avatar=msg_avatar
    ):

        st.markdown(
            f"**{html.escape(msg_user)}**"
        )

        if msg_kind == "text":

            st.markdown(
                html.escape(msg_body or "")
            )

        elif msg_kind == "gif":

            st.image(
                msg_body,
                width=280
            )

        elif msg_kind == "image" and msg_image:

            st.image(
                msg_image,
                width=280
            )

            if msg_body:

                st.caption(msg_body)

        st.caption(
            time_text(msg_created)
        )


# ==========================================
# CHAT INPUT
# ==========================================

user_input = st.chat_input(
    "Write a message..."
)

if user_input and user_input.strip():

    save_message(
        room,
        username,
        avatar,
        "text",
        user_input.strip()
    )

    st.rerun()


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "⚡ Aysuu Messenger • Made for your people"
)

st.caption(
    "Keep your room name private if you don't want "
    "others to discover your conversation."
)
