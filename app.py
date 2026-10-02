import streamlit as st
from datetime import datetime
import base64

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ChatSpace // Ghost",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLEAN MODERN CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: radial-gradient(circle at 10% 20%, #0f172a 0%, #020617 100%);
    color: #f8fafc;
}
[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
    backdrop-filter: blur(20px);
}
.chat-bubble {
    padding: 12px 16px;
    border-radius: 16px;
    margin-bottom: 10px;
    max-width: 82%;
    word-break: break-word;
}
.my-msg {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #ffffff;
    margin-left: auto;
    border-bottom-right-radius: 2px;
}
.other-msg {
    background: rgba(30, 41, 59, 0.95);
    color: #f1f5f9;
    margin-right: auto;
    border-bottom-left-radius: 2px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.bubble-meta {
    font-size: 0.72rem;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 4px;
    opacity: 0.85;
}
.bubble-body {
    font-size: 0.95rem;
    line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

# --- GLOBAL STORE ---
@st.cache_resource
def get_global_store():
    return {}

chat_rooms = get_global_store()

STICKERS = [
    {"name": "🔥 Fire", "url": "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"},
    {"name": "😂 Laugh", "url": "https://media.giphy.com/media/26n6Gx9moCgs1DflG/giphy.gif"},
    {"name": "❤️ Love", "url": "https://media.giphy.com/media/R6gVNROjBy4UM/giphy.gif"},
    {"name": "😎 Cool", "url": "https://media.giphy.com/media/jpbnoe3UIa8TU8LM13/giphy.gif"},
    {"name": "🎉 Party", "url": "https://media.giphy.com/media/blSTtZehjAZ8I/giphy.gif"},
    {"name": "👀 Shock", "url": "https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif"},
]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚡ **ChatSpace Ultra**")
    st.caption("🔒 End-to-End Ghost Chat")
    st.divider()

    username = st.text_input("👤 Your Alias", placeholder="e.g. Alex", max_chars=18)
    room_id = st.text_input("🔑 Room Key", placeholder="e.g. VIP-777", type="password")

    if room_id:
        if room_id not in chat_rooms:
            chat_rooms[room_id] = []
        user_count = len({m["user"] for m in chat_rooms[room_id]})
        st.metric(label="Active in Room", value=max(user_count, 1))

    if st.button("🗑️ Clear Room Chat", use_container_width=True):
        if room_id in chat_rooms:
            chat_rooms[room_id] = []
            st.rerun()

# --- MAIN UI ---
if not username or not room_id:
    st.info("👈 Upar left arrow (`>>`) daba kar apna **Alias** aur **Room Key** enter kijiye!")
else:
    if room_id not in chat_rooms:
        chat_rooms[room_id] = []

    st.markdown(f"#### 🔒 Room: `{room_id}` | Connected as **{username}**")

    # Render Chat List
    chat_box = st.container()
    with chat_box:
        if not chat_rooms[room_id]:
            st.caption("💬 Is room mein abhi koi message nahi hai. Hi bolo!")
        else:
            for msg in chat_rooms[room_id]:
                is_me = (msg["user"] == username)
                b_class = "my-msg" if is_me else "other-msg"
                user_label = "You" if is_me else msg["user"]

                # Single-line zero-indent HTML string to prevent markdown code block bug
                if msg["type"] == "text":
                    html = f'<div class="chat-bubble {b_class}"><div class="bubble-meta"><span>{user_label}</span><span>{msg["time"]}</span></div><div class="bubble-body">{msg["content"]}</div></div>'
                    st.markdown(html, unsafe_allow_html=True)
                elif msg["type"] == "gif":
                    html = f'<div class="chat-bubble {b_class}"><div class="bubble-meta"><span>{user_label}</span><span>{msg["time"]}</span></div><img src="{msg["content"]}" style="width:100%; border-radius:10px; margin-top:4px;" /></div>'
                    st.markdown(html, unsafe_allow_html=True)
                elif msg["type"] == "image":
                    html = f'<div class="chat-bubble {b_class}"><div class="bubble-meta"><span>{user_label}</span><span>{msg["time"]}</span></div><img src="data:image/jpeg;base64,{msg["content"]}" style="width:100%; border-radius:10px; margin-top:4px;" /></div>'
                    st.markdown(html, unsafe_allow_html=True)

    # --- PHOTO & GIF PANEL ---
    with st.expander("✨ Photo • Sticker • GIF"):
        tab1, tab2 = st.tabs(["📷 Photo", "🎭 Stickers"])
        with tab1:
            up_file = st.file_uploader("Select image", type=["png", "jpg", "jpeg", "webp"], key="img_uploader")
            if up_file is not None:
                if st.button("🚀 Send Photo", use_container_width=True):
                    b64_img = base64.b64encode(up_file.read()).decode()
                    chat_rooms[room_id].append({
                        "user": username,
                        "type": "image",
                        "content": b64_img,
                        "time": datetime.now().strftime("%I:%M %p")
                    })
                    st.rerun()

        with tab2:
            cols = st.columns(3)
            for idx, stk in enumerate(STICKERS):
                with cols[idx % 3]:
                    st.image(stk["url"], width=60)
                    if st.button(stk["name"], key=f"stk_{idx}", use_container_width=True):
                        chat_rooms[room_id].append({
                            "user": username,
                            "type": "gif",
                            "content": stk["url"],
                            "time": datetime.now().strftime("%I:%M %p")
                        })
                        st.rerun()

    # --- INPUT FORM ---
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 2])
        with col1:
            txt = st.text_input("Type your private message...", label_visibility="collapsed")
        with col2:
            submit = st.form_submit_button("Send 🚀", use_container_width=True)

        if submit and txt.strip():
            chat_rooms[room_id].append({
                "user": username,
                "type": "text",
                "content": txt.strip(),
                "time": datetime.now().strftime("%I:%M %p")
            })
            st.rerun()
