import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh


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
# AUTOMATIC REFRESH
# =========================================================

# Chat automatically checks for new messages every 2 seconds.
# User ko koi Sync button nahi chahiye.

st_autorefresh(
    interval=2000,
    key="chat_auto_refresh"
)


# =========================================================
# MODERN CSS
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
    background: rgba(15, 23, 42, 0.96) !important;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SHARED CHAT STORE
# =========================================================

@st.cache_resource
def get_chat_rooms():

    return {}


chat_rooms = get_chat_rooms()


# =========================================================
# STICKERS / GIFS
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


    # -----------------------------------------------------
    # USER NAME
    # -----------------------------------------------------

    username = st.text_input(
        "👤 Your Alias",
        placeholder="e.g. Aham",
        max_chars=18
    ).strip()


    # -----------------------------------------------------
    # ROOM KEY
    # -----------------------------------------------------

    room_id = st.text_input(
        "🔑 Room Key",
        placeholder="e.g. friends123",
        type="password"
    ).strip().lower()


    # -----------------------------------------------------
    # ROOM
    # -----------------------------------------------------

    if room_id:

        if room_id not in chat_rooms:

            chat_rooms[room_id] = []

        st.success(
            f"Room: #{room_id}"
        )

        st.metric(
            "💬 Messages",
            len(chat_rooms[room_id])
        )


    st.divider()


    # -----------------------------------------------------
    # CLEAR ROOM
    # -----------------------------------------------------

    if st.button(
        "🗑️ Clear Room Chat",
        use_container_width=True
    ):

        if room_id in chat_rooms:

            chat_rooms[room_id] = []

            st.rerun()


# =========================================================
# LOGIN SCREEN
# =========================================================

if not username or not room_id:

    st.info(
        "👈 Sidebar mein apna Alias aur Room Key enter karo."
    )

    st.markdown("""
    ### ⚡ ChatSpace Ultra

    👤 **Apna naam alag rakho**

    🔑 **Dono log same Room Key use karo**

    💬 **Messages automatically refresh honge**

    📷 **Photos supported**

    🎭 **GIFs & Stickers supported**

    💬 **Maximum 500 messages**
    """)

    st.stop()


# =========================================================
# CREATE ROOM IF NEEDED
# =========================================================

if room_id not in chat_rooms:

    chat_rooms[room_id] = []


messages = chat_rooms[room_id]


# =========================================================
# HEADER
# =========================================================

st.markdown(
    f"#### 🔒 Private Room: `#{room_id}`"
)

st.caption(
    f"Connected as **{username}** • "
    f"{len(messages)}/500 messages"
)

st.divider()


# =========================================================
# DISPLAY CHAT
# =========================================================

if not messages:

    st.info(
        "💬 No messages yet. "
        "Start the conversation!"
    )

else:

    for msg in messages:

        is_me = (
            msg["user"] == username
        )

        avatar = (
            "👤"
            if is_me
            else "💬"
        )

        role = (
            "user"
            if is_me
            else "assistant"
        )


        with st.chat_message(
            role,
            avatar=avatar
        ):

            st.markdown(
                f"**{msg['user']}** • "
                f"*{msg['time']}*"
            )


            # -------------------------------------------------
            # TEXT MESSAGE
            # -------------------------------------------------

            if msg["type"] == "text":

                st.write(
                    msg["content"]
                )


            # -------------------------------------------------
            # GIF / STICKER
            # -------------------------------------------------

            elif msg["type"] == "gif":

                st.image(
                    msg["content"],
                    width=220
                )


            # -------------------------------------------------
            # PHOTO
            # -------------------------------------------------

            elif msg["type"] == "image":

                st.image(
                    msg["content"],
                    width=500
                )


# =========================================================
# PHOTO + GIF PANEL
# =========================================================

with st.expander(
    "✨ Photo • Sticker • GIF"
):

    tab_photo, tab_sticker = st.tabs(
        [
            "📷 Upload Photo",
            "🎭 GIFs & Stickers"
        ]
    )


    # =====================================================
    # PHOTO TAB
    # =====================================================

    with tab_photo:

        uploaded = st.file_uploader(
            "Select Photo",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="photo_upload"
        )


        if uploaded:

            st.image(
                uploaded,
                width=300
            )


            if st.button(
                "🚀 Send Photo",
                use_container_width=True
            ):

                image_bytes = uploaded.getvalue()


                chat_rooms[room_id].append({

                    "user": username,

                    "type": "image",

                    "content": image_bytes,

                    "time": datetime.now().strftime(
                        "%I:%M %p"
                    )

                })


                # Keep latest 500 messages only

                if len(chat_rooms[room_id]) > 500:

                    chat_rooms[room_id].pop(0)


                st.rerun()


    # =====================================================
    # GIF / STICKER TAB
    # =====================================================

    with tab_sticker:

        cols = st.columns(3)


        for index, sticker in enumerate(STICKERS):

            with cols[index % 3]:

                st.image(
                    sticker["url"],
                    width=75
                )


                if st.button(
                    sticker["name"],
                    key=f"sticker_{index}",
                    use_container_width=True
                ):

                    chat_rooms[room_id].append({

                        "user": username,

                        "type": "gif",

                        "content": sticker["url"],

                        "time": datetime.now().strftime(
                            "%I:%M %p"
                        )

                    })


                    # Keep latest 500 messages

                    if len(chat_rooms[room_id]) > 500:

                        chat_rooms[room_id].pop(0)


                    st.rerun()


# =========================================================
# MESSAGE INPUT
# =========================================================

with st.form(
    "message_form",
    clear_on_submit=True
):

    col1, col2 = st.columns(
        [8, 2]
    )


    with col1:

        message = st.text_input(
            "Message",
            placeholder="Type your message...",
            label_visibility="collapsed",
            max_chars=2000
        )


    with col2:

        send = st.form_submit_button(
            "🚀 Send",
            use_container_width=True
        )


    if send and message.strip():

        chat_rooms[room_id].append({

            "user": username,

            "type": "text",

            "content": message.strip(),

            "time": datetime.now().strftime(
                "%I:%M %p"
            )

        })


        # Keep latest 500 messages

        if len(chat_rooms[room_id]) > 500:

            chat_rooms[room_id].pop(0)


        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "⚡ ChatSpace Ultra • "
    "500 Message Limit • "
    "Automatic Refresh • "
    "Photos • GIFs • Stickers • No SQL"
)
