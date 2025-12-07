"""
AI Murder Mystery: The Blackwood Mansion
Streamlit Web UI
"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from murder_mystery import (
    MurderMysteryGame,
    SUSPECTS,
    CASE_FILE,
    VALID_WEAPONS,
    VALID_MOTIVES,
)

# Page config
st.set_page_config(
    page_title="AI Murder Mystery",
    page_icon="🔍",
    layout="wide",
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #8B0000;
        font-family: 'Georgia', serif;
    }
    .suspect-card {
        background-color: #1a1a2e;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .chat-message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user-message {
        background-color: #2d3748;
        text-align: right;
    }
    .suspect-message {
        background-color: #1a365d;
    }
    .case-file {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #8B0000;
    }
    .score-display {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "game" not in st.session_state:
        st.session_state.game = MurderMysteryGame()
    if "messages" not in st.session_state:
        st.session_state.messages = {sid: [] for sid in SUSPECTS.keys()}
    if "current_suspect" not in st.session_state:
        st.session_state.current_suspect = "s1"
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "accusation_result" not in st.session_state:
        st.session_state.accusation_result = None


def reset_game():
    """Reset the game state."""
    st.session_state.game = MurderMysteryGame()
    st.session_state.messages = {sid: [] for sid in SUSPECTS.keys()}
    st.session_state.current_suspect = "s1"
    st.session_state.game_over = False
    st.session_state.accusation_result = None


def render_case_briefing():
    """Render the case briefing section."""
    v = CASE_FILE["victim"]

    st.markdown("""
    <div class="case-file">
        <h3>📁 CASE BRIEFING</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Victim:** {v['name']}")
        st.markdown(f"**Time of Death:** {v['time_of_death']}")
    with col2:
        st.markdown(f"**Location:** {v['location']}")
        st.markdown(f"**Cause:** {v['cause']}")

    st.markdown("---")
    st.markdown("*Interrogate the suspects to discover WHO committed the murder, with WHAT weapon, and WHY.*")


def render_suspect_selector():
    """Render suspect selection sidebar."""
    st.sidebar.markdown("## 👥 Suspects")

    for sid, suspect in SUSPECTS.items():
        interviewed = sid in st.session_state.game.state.suspects_interviewed
        status = "✅" if interviewed else "⬜"

        if st.sidebar.button(
            f"{status} {suspect.name}",
            key=f"suspect_{sid}",
            use_container_width=True,
            disabled=st.session_state.game_over
        ):
            st.session_state.current_suspect = sid
            st.session_state.game.switch_suspect(sid)
            st.rerun()

    # Show current suspect
    current = SUSPECTS[st.session_state.current_suspect]
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Currently interrogating:**")
    st.sidebar.markdown(f"### {current.name}")


def render_game_status():
    """Render game status in sidebar."""
    state = st.session_state.game.state

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📊 Investigation Status")

    # Turn counter with progress bar
    progress = state.total_turns / state.max_turns
    st.sidebar.progress(progress)
    st.sidebar.markdown(f"**Turns:** {state.total_turns} / {state.max_turns}")

    # Suspects interviewed
    st.sidebar.markdown(f"**Suspects interviewed:** {len(state.suspects_interviewed)} / 3")

    # Warning if running low on turns
    if state.total_turns >= state.max_turns - 5 and not st.session_state.game_over:
        st.sidebar.warning(f"⚠️ Only {state.max_turns - state.total_turns} turns left!")


def render_chat_interface():
    """Render the main chat interface."""
    current_suspect = SUSPECTS[st.session_state.current_suspect]

    st.markdown(f"### 🗣️ Interrogating: {current_suspect.name}")

    # Chat container
    chat_container = st.container(height=400)

    with chat_container:
        messages = st.session_state.messages[st.session_state.current_suspect]

        if not messages:
            st.markdown(f"*{current_suspect.name} sits across from you, waiting for your questions...*")

        for msg in messages:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["content"])
            else:
                st.chat_message("assistant", avatar="🎭").markdown(msg["content"])

    # Input
    if not st.session_state.game_over:
        if st.session_state.game.state.total_turns >= st.session_state.game.state.max_turns:
            st.warning("⏰ No turns remaining! Make your accusation now.")
        else:
            user_input = st.chat_input(f"Ask {current_suspect.name} a question...")

            if user_input:
                # Add user message
                st.session_state.messages[st.session_state.current_suspect].append({
                    "role": "user",
                    "content": user_input
                })

                # Get response
                with st.spinner(f"{current_suspect.name} is thinking..."):
                    response = st.session_state.game.interrogate(user_input)

                # Add suspect response
                st.session_state.messages[st.session_state.current_suspect].append({
                    "role": "assistant",
                    "content": response
                })

                st.rerun()


def render_accusation_form():
    """Render the accusation form."""
    st.markdown("---")
    st.markdown("## ⚖️ Make Your Accusation")

    if st.session_state.game_over:
        st.info("Game over! Click 'New Game' to play again.")
        return

    with st.expander("Ready to accuse? Click here", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            accused = st.selectbox(
                "Who is the killer?",
                options=list(SUSPECTS.keys()),
                format_func=lambda x: SUSPECTS[x].name
            )

        with col2:
            weapon = st.selectbox(
                "Murder weapon?",
                options=VALID_WEAPONS
            )

        with col3:
            motive = st.selectbox(
                "Motive?",
                options=VALID_MOTIVES
            )

        st.warning("⚠️ This is your FINAL accusation. Choose carefully!")

        if st.button("🔨 Submit Accusation", type="primary", use_container_width=True):
            with st.spinner("The judge is reviewing your accusation..."):
                won, score, eval_text = st.session_state.game.make_accusation(accused, weapon, motive)

            st.session_state.game_over = True
            st.session_state.accusation_result = {
                "won": won,
                "score": score,
                "eval_text": eval_text
            }
            st.rerun()


def render_game_result():
    """Render the game result screen."""
    if not st.session_state.accusation_result:
        return

    result = st.session_state.accusation_result

    st.markdown("---")

    if result["won"]:
        st.balloons()
        st.success("# 🎉 CASE SOLVED!")
    else:
        st.error("# ❌ CASE UNSOLVED")
        st.markdown("*The killer remains free...*")

    # Score display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="score-display">
            {result['score']}/100
        </div>
        """, unsafe_allow_html=True)

    # Detailed evaluation
    with st.expander("📋 Case Resolution Details", expanded=True):
        st.markdown(result["eval_text"])

    # Play again button
    if st.button("🔄 New Game", type="primary", use_container_width=True):
        reset_game()
        st.rerun()


def main():
    """Main app function."""
    # Check for API key
    if not os.environ.get("GROQ_API_KEY"):
        st.error("⚠️ GROQ_API_KEY not set!")
        st.markdown("""
        Please set your Groq API key:
        ```bash
        export GROQ_API_KEY="your-api-key"
        streamlit run app.py
        ```

        Or add it to a `.env` file in the project directory.
        """)

        # Allow manual input
        api_key = st.text_input("Or enter your GROQ API key here:", type="password")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("API key set! Refresh the page to start.")
            st.rerun()
        return

    # Initialize session state
    init_session_state()

    # Header
    st.markdown("<h1 class='main-header'>🔍 AI Murder Mystery</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='main-header'>The Blackwood Mansion</h3>", unsafe_allow_html=True)

    # Sidebar
    render_suspect_selector()
    render_game_status()

    # New game button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 New Game", use_container_width=True):
        reset_game()
        st.rerun()

    # Main content
    render_case_briefing()

    # Show result if game is over
    if st.session_state.game_over and st.session_state.accusation_result:
        render_game_result()
    else:
        render_chat_interface()
        render_accusation_form()


if __name__ == "__main__":
    main()
