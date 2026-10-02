import streamlit as st
from datetime import datetime

# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="ChatSpace // Ghost",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# MODERN STYLING
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

* {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 20%,
            #0f172a 0%,
            #020617 100%
        );
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.95) !important;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# CENTRAL MEMORY VAULT
# =========================================================

class CentralVault:

    def __init__(self):
        self.rooms = {}

    def get_messages(self, room_id):

        return self.rooms.get(room_id, [])

    def add_message(self, room_id, message):

        if room_id not in self.rooms:
            self.rooms[room_id] = []

        self.rooms[room_id].append(message)

        # Maximum 100 messages per room
        if len(self.rooms[room_id]) > 100:
            self.rooms[room_id].pop(0)

    def clear(self, room_id):

        if room_id in self.rooms:
            self.rooms[room_id] = []


@st.cache_resource
def get_vault():

    return CentralVault()


vault = get_vault()


# =========================================================
# STICKERS
# =========================================================

STICKERS = [

    {
        "name": "🔥 Fire",
        "url": "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
    },

    {
        "name": "😂 Laugh",
        "url": "https://media.giphy.com/media/26n6Gx9moCgs1DflG/giphy.gif"
    },

    {
        "name": "❤️ Love",
        "url": "https://media.giphy.com/media/R6gVNROjBy4UM/giphy.gif"
    },

    {
        "name": "😎 Cool",
        "url": "https://media.giphy.com/media/jpbnoe3UIa8TU8LM13/giphy.gif"
    },

    {
        "name": "🎉 Party",
        "url": "https://media.giphy.com/media/blSTtZehjAZ8I/giphy.gif"
    },

    {
        "name": "👀 Shock",
        "url": "https://media.giphy.com/media/5VKbvrjxpVJCM/giphy.gif"
    }
]


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("### ⚡ **ChatSpace Ultra**")

    st.caption(
        "🔒 Private Multi-Device Chat"
    )

    st.divider()

    input_user = st.text_input(
        "👤 Your Alias",
        placeholder="e.g. Alex",
        max_chars=18
    )

    input_room = st.text_input(
        "🔑 Room Key",
        placeholder="e.g. secret77",
        type="password"
    )

    username = input_user.strip()

    room_id = input_room.strip().lower()

    # -----------------------------------------------------
    # ROOM INFO
    # -----------------------------------------------------

    if room_id:

        if room_id not in vault.rooms:

            vault.rooms[room_id] = []

        st.success(
            f"Connected to Room: #{room_id}"
        )

        st.metric(
            "💬 Messages",
            len(vault.get_messages(room_id))
        )

    st.divider()

    # -----------------------------------------------------
    # MANUAL SYNC
    # -----------------------------------------------------

    if st.button(
        "🔄 Sync Chat Now",
        use_container_width=True
    ):

        st.rerun()

    # -----------------------------------------------------
    # CLEAR ROOM
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear Room Chat",
        use_container_width=True
    ):

        if room_id:

            vault.clear(room_id)

            st.rerun()


# =========================================================
# LOGIN / ROOM SCREEN
# =========================================================

if not username or not room_id:

    st.info(
        "👈 Sidebar mein apna **Alias** aur **Room Key** daaliye!"
    )

    st.markdown("""
    ### 🔐 ChatSpace Ultra

    **How to use:**

    1. Apna alias enter karo.
    2. Dono log **same Room Key** enter karo.
    3. Same room mein chat karo.
    4. Naya message dekhne ke liye **Sync Chat Now** dabao.

    💬 Maximum 100 messages per room.
    """)

    st.stop()


# =========================================================
# MAIN CHAT HEADER
# =========================================================

st.markdown(
    f"#### 🔒 Private Vault: `#{room_id}`"
)

st.caption(
    f"Connected as **{username}**"
)

st.divider()


# =========================================================
# GET MESSAGES
# =========================================================

messages = vault.get_messages(room_id)


# =========================================================
# CHAT DISPLAY
# =========================================================

if not messages:

    st.info(
        "💬 Is room mein abhi koi message nahi hai. "
        "Hi bolo ya photo bhejo!"
    )

else:

    for msg in messages:

        is_me = (
            msg["user"] == username
        )

        avatar = "👤" if is_me else "💬"

        role = "user" if is_me else "assistant"

        with st.chat_message(
            role,
            avatar=avatar
        ):

            st.markdown(
                f"**{msg['user']}** • *{msg['time']}*"
            )

            # ---------------- TEXT ----------------

            if msg["type"] == "text":

                st.write(
                    msg["content"]
                )

            # ---------------- GIF ----------------

            elif msg["type"] == "gif":

                st.image(
                    msg["content"],
                    width=200
                )

            # ---------------- PHOTO ----------------

            elif msg["type"] == "image":

                st.image(
                    msg["content"],
                    width=500
                )


# =========================================================
# PHOTO + STICKERS
# =========================================================

with st.expander(
    "✨ Photo • Sticker • GIF"
):

    tab1, tab2 = st.tabs(
        [
            "📷 Upload Photo",
            "🎭 Stickers"
        ]
    )

    # =====================================================
    # PHOTO
    # =====================================================

    with tab1:

        up_file = st.file_uploader(
            "Select image",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="img_uploader"
        )

        if up_file is not None:

            st.image(
                up_file,
                width=300
            )

            if st.button(
                "🚀 Send Photo",
                use_container_width=True
            ):

                img_bytes = up_file.getvalue()

                vault.add_message(
                    room_id,
                    {
                        "user": username,
                        "type": "image",
                        "content": img_bytes,
                        "time": datetime.now().strftime(
                            "%I:%M %p"
                        )
                    }
                )

                st.rerun()

    # =====================================================
    # STICKERS
    # =====================================================

    with tab2:

        cols = st.columns(3)

        for idx, sticker in enumerate(STICKERS):

            with cols[idx % 3]:

                st.image(
                    sticker["url"],
                    width=70
                )

                if st.button(
                    sticker["name"],
                    key=f"sticker_{idx}",
                    use_container_width=True
                ):

                    vault.add_message(
                        room_id,
                        {
                            "user": username,
                            "type": "gif",
                            "content": sticker["url"],
                            "time": datetime.now().strftime(
                                "%I:%M %p"
                            )
                        }
                    )

                    st.rerun()


# =========================================================
# MESSAGE INPUT
# =========================================================

with st.form(
    "input_form",
    clear_on_submit=True
):

    col1, col2 = st.columns(
        [8, 2]
    )

    with col1:

        txt = st.text_input(
            "Type message...",
            label_visibility="collapsed",
            placeholder="Type your message..."
        )

    with col2:

        submit = st.form_submit_button(
            "Send 🚀",
            use_container_width=True
        )

    if submit and txt.strip():

        vault.add_message(
            room_id,
            {
                "user": username,
                "type": "text",
                "content": txt.strip(),
                "time": datetime.now().strftime(
                    "%I:%M %p"
                )
            }
        )

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚡ ChatSpace Ultra • Private Room • "
    "100 Message Limit • Manual Sync • No SQL"
)
