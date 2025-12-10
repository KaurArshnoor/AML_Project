"""
AI Murder Mystery: The Blackwood Mansion
Streamlit Web UI with Dark Noir Theme
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
    initial_sidebar_state="expanded",
)

# Dark Noir Theme CSS
st.markdown("""
<style>
    /* Import typewriter font */
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime:wght@400;700&display=swap');

    /* Global dark theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 50%, #0d0d0d 100%);
    }

    /* Main header - blood red */
    .main-header {
        text-align: center;
        color: #8B0000;
        font-family: 'Special Elite', cursive;
        text-shadow: 2px 2px 4px #000000;
        letter-spacing: 3px;
    }

    .sub-header {
        text-align: center;
        color: #666666;
        font-family: 'Courier Prime', monospace;
        font-style: italic;
    }

    /* Case file styling */
    .case-file {
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        padding: 25px;
        border-radius: 5px;
        border-left: 4px solid #8B0000;
        border-top: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        font-family: 'Courier Prime', monospace;
    }

    .case-file h3 {
        color: #8B0000;
        font-family: 'Special Elite', cursive;
        letter-spacing: 2px;
    }

    /* Suspect cards */
    .suspect-card {
        background: linear-gradient(145deg, #1a1a1a, #252525);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #333;
        transition: all 0.3s ease;
    }

    .suspect-card:hover {
        border-color: #8B0000;
        box-shadow: 0 0 10px rgba(139, 0, 0, 0.3);
    }

    /* Chat messages */
    .stChatMessage {
        background-color: #1a1a1a !important;
        border: 2px solid #8B0000;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.6);
        font-family: 'Courier Prime', monospace;
    }

    /* Stronger outline for user and assistant chat bubbles */
    .stChatMessage > div {
        border-radius: 8px;
    }

    /* Typewriter text effect */
    .typewriter-text {
        font-family: 'Special Elite', cursive;
        color: #c0c0c0;
        line-height: 1.8;
    }

    /* Notes section */
    .detective-notes {
        background: linear-gradient(145deg, #2a2a1a, #1a1a0a);
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #4a4a2a;
        font-family: 'Courier Prime', monospace;
        min-height: 150px;
    }

    .notes-header {
        color: #8B0000;
        font-family: 'Special Elite', cursive;
        border-bottom: 1px solid #4a4a2a;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }

    /* Score display */
    .score-display {
        font-size: 64px;
        font-weight: bold;
        text-align: center;
        color: #8B0000;
        font-family: 'Special Elite', cursive;
        text-shadow: 2px 2px 4px #000000;
    }

    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d0d, #1a1a1a);
    }

    .sidebar-header {
        color: #8B0000;
        font-family: 'Special Elite', cursive;
        letter-spacing: 2px;
        text-align: center;
        padding: 10px;
        border-bottom: 1px solid #333;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(145deg, #2d2d2d, #1a1a1a);
        color: #c0c0c0;
        border: 1px solid #444;
        font-family: 'Courier Prime', monospace;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        border-color: #8B0000;
        color: #8B0000;
        box-shadow: 0 0 10px rgba(139, 0, 0, 0.3);
    }

    /* Primary button (accusation) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(145deg, #8B0000, #5a0000);
        color: #ffffff;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(145deg, #a00000, #6a0000);
        box-shadow: 0 0 15px rgba(139, 0, 0, 0.5);
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #8B0000;
        font-family: 'Special Elite', cursive;
    }

    /* Progress bar */
    .stProgress > div > div {
        background-color: #8B0000;
    }

    /* Warning/Info boxes */
    .stWarning {
        background-color: rgba(139, 0, 0, 0.2);
        border-left-color: #8B0000;
    }

    /* Text inputs */
    .stTextArea textarea, .stTextInput input, .stChatInput textarea, .stChatInput input {
        background-color: #141414 !important;
        color: #c0c0c0 !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-family: 'Courier Prime', monospace;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }

    /* Ensure the chat input area matches the noir theme */
    .stChatInput, .stChatInput > div {
        background: transparent !important;
    }

    /* Chat input outer container: ensure parent panel is dark (covers white container issue) */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    .stChatInput, .stChatInput > div,
    .stChatInput .css-1v3fvcr,
    .stChatInput .css-1d391kg,
    .stChatInput .css-18e3th9 {
        background: linear-gradient(180deg, #0d0d0d, #141414) !important;
        color: #c0c0c0 !important;
        border-radius: 10px !important;
        padding: 6px !important;
        border: 1px solid #222 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6) !important;
    }

    /* Make the top page container and any light boxes darker to match theme */
    .block-container, .css-1y4p8pa, .main, header, .stApp > div {
        background: transparent !important;
    }

    /* Force body and root containers to dark background to eliminate remaining white areas */
    html, body, .stApp, .reportview-container, .appview-container, .main, .block-container, .block-container > div {
        background: linear-gradient(180deg, #0a0a0a 0%, #141414 60%, #0d0d0d 100%) !important;
        color: #c0c0c0 !important;
    }

    /* Catch-all for Streamlit autogenerated panel classes that may render white backgrounds */
    [class^="css-"] {
        background-repeat: no-repeat !important;
    }

    /* Specifically darken the app footer and any full-width white strips */
    footer, .stFooter, .css-1lsmgbg, .css-1e0g9af {
        background: linear-gradient(180deg, #0a0a0a, #141414) !important;
        color: #c0c0c0 !important;
    }

    /* Tweak commonly-used Streamlit container classes to avoid white panels */
    .css-1fdrf8s, .css-18e3th9, .css-1v3fvcr, .css-1d391kg {
        background: linear-gradient(180deg, #0d0d0d, #1a1a1a) !important;
        color: #c0c0c0 !important;
    }

    /* Rain effect overlay */
    .rain-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cline x1='10' y1='0' x2='10' y2='100' stroke='%23ffffff08' stroke-width='1'/%3E%3Cline x1='30' y1='0' x2='30' y2='100' stroke='%23ffffff05' stroke-width='1'/%3E%3Cline x1='50' y1='0' x2='50' y2='100' stroke='%23ffffff08' stroke-width='1'/%3E%3Cline x1='70' y1='0' x2='70' y2='100' stroke='%23ffffff05' stroke-width='1'/%3E%3Cline x1='90' y1='0' x2='90' y2='100' stroke='%23ffffff08' stroke-width='1'/%3E%3C/svg%3E");
        opacity: 0.3;
        z-index: -1;
    }

    /* Fog effect at bottom */
    .fog-overlay {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 150px;
        background: linear-gradient(to top, rgba(10,10,10,0.8), transparent);
        pointer-events: none;
        z-index: 1;
    }

    /* Vignette effect */
    .vignette {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.6) 100%);
        z-index: 0;
    }
</style>

<!-- Atmospheric overlays -->
<div class="vignette"></div>
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
    # Notes for each suspect
    if "notes" not in st.session_state:
        st.session_state.notes = {sid: "" for sid in SUSPECTS.keys()}
    # General notes
    if "general_notes" not in st.session_state:
        st.session_state.general_notes = ""


def reset_game():
    """Reset the game state."""
    st.session_state.game = MurderMysteryGame()
    st.session_state.messages = {sid: [] for sid in SUSPECTS.keys()}
    st.session_state.current_suspect = "s1"
    st.session_state.game_over = False
    st.session_state.accusation_result = None
    st.session_state.notes = {sid: "" for sid in SUSPECTS.keys()}
    st.session_state.general_notes = ""


def render_case_briefing():
    """Render the case briefing section."""
    v = CASE_FILE["victim"]

    st.markdown("""
    <div class="case-file">
        <h3>📁 CLASSIFIED CASE FILE</h3>
        <p style="color: #666; font-size: 12px;">BLACKWOOD MANSION HOMICIDE - FILE #1947</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**VICTIM:** {v['name']}")
        st.markdown(f"**TIME OF DEATH:** {v['time_of_death']}")
    with col2:
        st.markdown(f"**LOCATION:** {v['location']}")
        st.markdown(f"**CAUSE:** {v['cause']}")

    st.markdown("---")
    st.markdown("*Your mission: Interrogate the suspects. Discover WHO committed the murder, with WHAT weapon, and WHY.*")


def render_suspect_selector():
    """Render suspect selection sidebar."""
    st.sidebar.markdown('<div class="sidebar-header">👥 SUSPECTS</div>', unsafe_allow_html=True)
    st.sidebar.markdown("")

    for sid, suspect in SUSPECTS.items():
        interviewed = sid in st.session_state.game.state.suspects_interviewed
        turns = st.session_state.game.state.turns_per_suspect.get(sid, 0)

        if interviewed:
            status = f"🔍 ({turns} questions)"
        else:
            status = "⬜ Not questioned"

        if st.sidebar.button(
            f"{suspect.name}\n{status}",
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
    st.sidebar.markdown(f"### 🎭 {current.name}")


def render_game_status():
    """Render game status in sidebar."""
    state = st.session_state.game.state

    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-header">📊 INVESTIGATION</div>', unsafe_allow_html=True)

    # Turn counter with progress bar
    progress = state.total_turns / state.max_turns
    st.sidebar.progress(progress)
    remaining = state.max_turns - state.total_turns
    st.sidebar.markdown(f"**Questions remaining:** {remaining}")

    # Suspects interviewed
    st.sidebar.markdown(f"**Suspects questioned:** {len(state.suspects_interviewed)} / 3")

    # Warning if running low on turns
    if remaining <= 5 and remaining > 0 and not st.session_state.game_over:
        st.sidebar.error(f"⚠️ Only {remaining} questions left!")
    elif remaining == 0 and not st.session_state.game_over:
        st.sidebar.error("🚨 Time's up! Make your accusation!")


def render_chat_interface():
    """Render the main chat interface."""
    current_suspect = SUSPECTS[st.session_state.current_suspect]

    st.markdown(f"""
    <div style="background: linear-gradient(90deg, transparent, #1a1a1a, transparent); padding: 10px; text-align: center;">
        <span style="font-family: 'Special Elite', cursive; font-size: 24px; color: #8B0000;">
            🎭 INTERROGATION ROOM
        </span>
        <br>
        <span style="font-family: 'Courier Prime', monospace; color: #666;">
            Subject: {current_suspect.name}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Chat container
    chat_container = st.container(height=400)

    with chat_container:
        messages = st.session_state.messages[st.session_state.current_suspect]

        if not messages:
            st.markdown(f"""
            <div class="typewriter-text" style="text-align: center; padding: 50px; color: #666;">
                <em>*{current_suspect.name} sits across the table, the dim light casting shadows across their face...*</em>
            </div>
            """, unsafe_allow_html=True)

        for msg in messages:
            if msg["role"] == "user":
                st.chat_message("user", avatar="🕵️").markdown(msg["content"])
            else:
                st.chat_message("assistant", avatar="🎭").markdown(f'*{msg["content"]}*')

    # Input
    if not st.session_state.game_over:
        if st.session_state.game.state.total_turns >= st.session_state.game.state.max_turns:
            st.error("🚨 No questions remaining! You must make your accusation now.")
        else:
            # Suggested prompt chips to help the player ask questions
            suggested_prompts = [
                "Where were you at the time of the murder?",
                "How do you know the victim?",
                "Did you see anyone suspicious that night?",
                "Can anyone corroborate your alibi?",
                "Why would someone want to hurt the victim?",
                "Did you have any disagreements with the victim?"
            ]

            st.markdown("**Suggested questions:**")

            # Render suggestion buttons in rows of up to 3 buttons
            chunk_size = 3
            for i in range(0, len(suggested_prompts), chunk_size):
                row = suggested_prompts[i:i+chunk_size]
                cols = st.columns(len(row))
                for j, prompt in enumerate(row):
                    # key must be unique per suspect to avoid collisions across suspects
                    btn_key = f"suggest_{st.session_state.current_suspect}_{i+j}"
                    if cols[j].button(prompt, key=btn_key):
                        # Add user message
                        st.session_state.messages[st.session_state.current_suspect].append({
                            "role": "user",
                            "content": prompt
                        })

                        # Get response from game and append
                        with st.spinner(f"*{current_suspect.name} considers your question...*"):
                            response = st.session_state.game.interrogate(prompt)

                        st.session_state.messages[st.session_state.current_suspect].append({
                            "role": "assistant",
                            "content": response
                        })

                        st.rerun()

            # Chat input with improved placeholder example
            user_input = st.chat_input(
                placeholder=f"Interrogate {current_suspect.name}... e.g., 'Where were you at the time of the murder?'"
            )

            if user_input:
                # Add user message
                st.session_state.messages[st.session_state.current_suspect].append({
                    "role": "user",
                    "content": user_input
                })

                # Get response
                with st.spinner(f"*{current_suspect.name} considers your question...*"):
                    response = st.session_state.game.interrogate(user_input)

                # Add suspect response
                st.session_state.messages[st.session_state.current_suspect].append({
                    "role": "assistant",
                    "content": response
                })

                st.rerun()


def render_notes_section():
    """Render the detective's notes section."""
    st.markdown("---")
    st.markdown("""
    <div class="notes-header">
        📝 DETECTIVE'S NOTES
    </div>
    """, unsafe_allow_html=True)

    # Tabs for different note sections
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📋 General Notes",
        f"🎭 {SUSPECTS['s1'].name}",
        f"🎭 {SUSPECTS['s2'].name}",
        f"🎭 {SUSPECTS['s3'].name}"
    ])

    with tab1:
        st.session_state.general_notes = st.text_area(
            "General observations and theories:",
            value=st.session_state.general_notes,
            height=150,
            placeholder="Write your theories here...\n\nExample:\n- The timeline doesn't add up\n- Someone is lying about their alibi\n- Check the library for clues",
            key="general_notes_input"
        )

    with tab2:
        st.session_state.notes["s1"] = st.text_area(
            f"Notes on {SUSPECTS['s1'].name}:",
            value=st.session_state.notes["s1"],
            height=150,
            placeholder=f"What did {SUSPECTS['s1'].name} reveal?\nAny suspicious behavior?",
            key="notes_s1"
        )

    with tab3:
        st.session_state.notes["s2"] = st.text_area(
            f"Notes on {SUSPECTS['s2'].name}:",
            value=st.session_state.notes["s2"],
            height=150,
            placeholder=f"What did {SUSPECTS['s2'].name} reveal?\nAny suspicious behavior?",
            key="notes_s2"
        )

    with tab4:
        st.session_state.notes["s3"] = st.text_area(
            f"Notes on {SUSPECTS['s3'].name}:",
            value=st.session_state.notes["s3"],
            height=150,
            placeholder=f"What did {SUSPECTS['s3'].name} reveal?\nAny suspicious behavior?",
            key="notes_s3"
        )


def render_accusation_form():
    """Render the accusation form."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <span style="font-family: 'Special Elite', cursive; font-size: 28px; color: #8B0000;">
            ⚖️ MAKE YOUR ACCUSATION
        </span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.game_over:
        st.info("The case is closed. Click 'New Case' to investigate another mystery.")
        return

    with st.expander("🔓 Ready to name the killer? Click here...", expanded=False):
        st.markdown("""
        <p style="font-family: 'Courier Prime', monospace; color: #888; text-align: center;">
            Choose wisely, detective. You only get one chance.
        </p>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**THE KILLER**")
            accused = st.selectbox(
                "Who committed the murder?",
                options=list(SUSPECTS.keys()),
                format_func=lambda x: SUSPECTS[x].name,
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**THE WEAPON**")
            weapon = st.selectbox(
                "What was the murder weapon?",
                options=VALID_WEAPONS,
                label_visibility="collapsed"
            )

        with col3:
            st.markdown("**THE MOTIVE**")
            motive = st.selectbox(
                "Why did they do it?",
                options=VALID_MOTIVES,
                label_visibility="collapsed"
            )

        st.markdown("")
        st.warning("⚠️ This is your FINAL accusation. There is no going back.")

        if st.button("🔨 I ACCUSE...", type="primary", use_container_width=True):
            with st.spinner("*The room falls silent as the evidence is reviewed...*"):
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
        st.markdown("""
        <div style="text-align: center; padding: 30px;">
            <span style="font-family: 'Special Elite', cursive; font-size: 48px; color: #228B22;">
                🎉 CASE SOLVED
            </span>
            <br><br>
            <span style="font-family: 'Courier Prime', monospace; color: #666;">
                Justice has been served. The killer is behind bars.
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 30px;">
            <span style="font-family: 'Special Elite', cursive; font-size: 48px; color: #8B0000;">
                ❌ CASE UNSOLVED
            </span>
            <br><br>
            <span style="font-family: 'Courier Prime', monospace; color: #666;">
                The killer walks free... for now.
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Score display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="score-display">
            {result['score']}/100
        </div>
        <p style="text-align: center; font-family: 'Courier Prime', monospace; color: #666;">
            DETECTIVE RATING
        </p>
        """, unsafe_allow_html=True)

    # Detailed evaluation
    with st.expander("📋 Case Resolution Report", expanded=True):
        st.markdown(result["eval_text"])

    # Play again button
    st.markdown("")
    if st.button("🔄 NEW CASE", type="primary", use_container_width=True):
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
    st.markdown("""
    <h1 class='main-header'>🔍 AI MURDER MYSTERY</h1>
    <h3 class='sub-header'>The Blackwood Mansion Affair</h3>
    <p style="text-align: center; color: #444; font-family: 'Courier Prime', monospace; font-size: 12px;">
        A game of deception, deduction, and dark secrets
    </p>
    """, unsafe_allow_html=True)

    # Sidebar
    render_suspect_selector()
    render_game_status()

    # New game button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 NEW CASE", use_container_width=True):
        reset_game()
        st.rerun()

    # Main content
    render_case_briefing()

    # Show result if game is over
    if st.session_state.game_over and st.session_state.accusation_result:
        render_game_result()
    else:
        render_chat_interface()
        render_notes_section()
        render_accusation_form()


if __name__ == "__main__":
    main()
