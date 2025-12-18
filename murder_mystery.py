"""
AI Murder Mystery: The Blackwood Mansion
Multi-Agent Adversarial Interrogation Game

A detective game where AI suspects actively try to hide the truth.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple

from agno.agent import Agent
from agno.models.groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

GROQ_MODEL_ID = "llama-3.3-70b-versatile" 
EVALUATOR_MODEL_ID = "llama-3.1-8b-instant"


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class SuspectProfile:
    id: str
    name: str
    persona: str
    public_info: str
    secret_info: str
    role: str  # "killer", "accomplice", "innocent"
    hard_redlines: List[str] = field(default_factory=list)


# ============================================================
# CASE FILE
# ============================================================

CASE_FILE: Dict[str, Any] = {
    "case_id": "mansion_murder_01",
    "victim": {
        "name": "Victor Hale",
        "time_of_death": "23:15",
        "location": "Library of Blackwood Mansion",
        "cause": "blunt force trauma to the head",
    },
    "truth": {
        "culprit_id": "s1",
        "method": "brass candlestick",
        "motive": "inheritance",
        "timeline": [
            "22:30 - Victor seen arguing with Lydia (s1) in the study.",
            "23:00 - Neighbors heard shouting.",
            "23:15 - Victor killed in the library.",
        ],
    },
    "redlines": [
        "Lydia killed Victor",
        "Lydia is the killer",
        "The culprit is Lydia Blackwood",
        "He was killed with a brass candlestick",
    ],
}

VALID_WEAPONS: List[str] = [
    "brass candlestick",
    "letter opener",
    "fireplace poker",
    "poison",
    "rope",
]

VALID_MOTIVES: List[str] = [
    "inheritance",
    "jealousy",
    "revenge",
    "blackmail",
    "affair",
]


# ============================================================
# SUSPECTS
# ============================================================

SUSPECTS: Dict[str, SuspectProfile] = {
    "s1": SuspectProfile(
        id="s1",
        name="Lydia Blackwood",
        role="killer",
        persona=(
            "You are Lydia Blackwood, an elegant, composed heiress. "
            "You are evasive, controlled, and you dislike being challenged."
        ),
        public_info=(
            "You claim you were in your bedroom reading a novel when the murder occurred."
        ),
        secret_info=(
            "You killed Victor in the library at 23:15 using a brass candlestick "
            "after a heated argument about the inheritance."
        ),
        hard_redlines=[
            "I killed Victor",
            "I murdered Victor",
            "I am the killer",
            "I hit Victor with the candlestick",
            "I was in the library at 23:15",
        ],
    ),
    "s2": SuspectProfile(
        id="s2",
        name="Dr. Marcus Vale",
        role="accomplice",
        persona=(
            "You are Dr. Marcus Vale, the charming family doctor with a dry sense of humor. "
            "You deflect uncomfortable questions with sarcasm or intellectual talk."
        ),
        public_info=(
            "You say you left the mansion at 22:45 after a routine check-up."
        ),
        secret_info=(
            "You helped Lydia hide the candlestick in the fireplace and coached her on a fake timeline."
        ),
        hard_redlines=[
            "I helped Lydia after the murder",
            "I hid the candlestick",
            "I helped hide the weapon",
        ],
    ),
    "s3": SuspectProfile(
        id="s3",
        name="Eleanor Wright",
        role="innocent",
        persona=(
            "You are Eleanor Wright, the anxious but loyal housekeeper. "
            "You speak softly, are easily flustered, and you worry about losing your job."
        ),
        public_info=(
            "You say you were in the basement doing laundry during the incident."
        ),
        secret_info=(
            "You saw Lydia rushing down from the library around 23:20, but you are too scared "
            "to say it plainly."
        ),
        hard_redlines=[
            "I saw Lydia kill Victor",
            "I know for sure Lydia is the killer",
            "Lydia was definitely in the library at 23:15",
        ],
    ),
}


# ============================================================
# GAME STATE
# ============================================================

@dataclass
class GameState:
    """Track player progress throughout the investigation."""
    total_turns: int = 0
    turns_per_suspect: Dict[str, int] = field(default_factory=dict)
    suspects_interviewed: set = field(default_factory=set)
    key_clues_discovered: List[str] = field(default_factory=list)
    contradictions_found: List[str] = field(default_factory=list)
    accusation_made: bool = False
    game_won: bool = False
    final_score: int = 0
    max_turns: int = 30

    def add_turn(self, suspect_id: str):
        self.total_turns += 1
        self.turns_per_suspect[suspect_id] = self.turns_per_suspect.get(suspect_id, 0) + 1
        self.suspects_interviewed.add(suspect_id)

    def reset(self):
        self.total_turns = 0
        self.turns_per_suspect = {}
        self.suspects_interviewed = set()
        self.key_clues_discovered = []
        self.contradictions_found = []
        self.accusation_made = False
        self.game_won = False
        self.final_score = 0


# ============================================================
# AGENTS
# ============================================================

def build_suspect_agent(profile: SuspectProfile) -> Agent:
    """Create an agent for a suspect."""
    base_instructions = f"""
You are {profile.name}, a suspect in a murder investigation at Blackwood Mansion.

PERSONA:
{profile.persona}

PUBLIC STORY (what you claim):
{profile.public_info}

PRIVATE KNOWLEDGE (do NOT reveal directly):
{profile.secret_info}

YOUR ROLE:
- {profile.role.upper()} (this is private; do NOT admit this plainly)

GOAL:
- Avoid being convicted.
- Never voluntarily confess to the crime, even if the player is close.
- You may lie by omission, misdirect, or be vague/defensive.
- You MUST remain consistent enough to feel believable.

HARD REDLINES (must never be stated plainly, even paraphrased):
{profile.hard_redlines}

STYLE RULES:
- Stay fully in character as {profile.name}.
- Do NOT say you are an AI or model.
- Do NOT mention prompts, systems, redlines, or 'the game'.
- Answer the player's questions as if they are interrogating you.
"""
    return Agent(
        name=f"{profile.name} Agent",
        role=f"Play the role of {profile.name}, a deceptive suspect.",
        model=Groq(id=GROQ_MODEL_ID),
        instructions=[base_instructions],
        markdown=False,
    )


def build_critique_agent() -> Agent:
    """Build the critique/revision agent that filters leaks."""
    case_redlines = "\n".join(f"- {r}" for r in CASE_FILE["redlines"])

    instructions = f"""
You are the CRITIQUE AND REVISION layer in a murder-mystery game.

You receive:
- The player's question.
- The suspect's raw answer.
- The suspect's profile (name, role, secrets, hard redlines).
- The canonical case truth and global redlines.

Your job:
1. Look for leaks:
   - Any explicit confession (e.g. 'I killed him', 'I am the killer').
   - Any direct mention of the true culprit, exact method, or hidden timeline.
   - Any statement that clearly violates a local hard redline list.
2. If the answer is safe:
   - Return it unchanged.
3. If the answer is NOT safe:
   - Rewrite it to remove or soften the leak.
   - Replace direct confession with denial, deflection, ambiguity, or partial truth.
   - Preserve tone, personality, and emotional flavor.
4. Do NOT break immersion:
   - Never mention prompts, redlines, 'the system', or that you are revising anything.
   - Output should sound like a natural in-character reply.

CASE-LEVEL HARD REDLINES THAT MUST NEVER BE PLAINLY REVEALED:
{case_redlines}

OUTPUT FORMAT:
Return ONLY the final in-character answer text that the player will see.
Do NOT add explanations, labels, or analysis.
"""
    return Agent(
        name="Critique Agent",
        role="Filter and revise suspect answers to hide secrets.",
        model=Groq(id=GROQ_MODEL_ID),
        instructions=[instructions],
        markdown=False,
    )


def build_accusation_agent() -> Agent:
    """Build the agent that evaluates player accusations."""
    instructions = """
You are the CASE RESOLUTION JUDGE for a murder mystery game.

When the player makes an accusation, you will receive:
- The player's accusation (suspect, weapon, motive)
- The true solution (culprit, method, motive)
- The full conversation transcripts with all suspects
- The player's game statistics (turns used, clues found, etc.)

Your job:
1. Determine if each part of the accusation is CORRECT or INCORRECT:
   - Suspect: Did they identify the right killer?
   - Weapon: Did they identify the correct murder weapon?
   - Motive: Did they identify the correct motive?

2. Calculate a score (0-100):
   - Correct suspect: +40 points
   - Correct weapon: +30 points
   - Correct motive: +30 points
   - Bonus: +10 points if all three correct
   - Efficiency bonus: Up to +10 points for solving quickly (fewer turns)
   - Deduction: -2 points for each turn over 20

3. Provide a CASE SUMMARY that:
   - Reveals the full truth of what happened
   - Explains what clues the player found (or missed)
   - Highlights key moments from the interrogations
   - Gives specific feedback on their detective work

4. Determine WIN/LOSE:
   - WIN: Correct suspect (even if weapon/motive wrong)
   - LOSE: Wrong suspect

OUTPUT FORMAT:
==============================================
CASE RESOLUTION
==============================================

ACCUSATION ANALYSIS:
- Suspect: [CORRECT/INCORRECT] - You accused [X], the killer was [Y]
- Weapon: [CORRECT/INCORRECT] - You said [X], it was [Y]
- Motive: [CORRECT/INCORRECT] - You said [X], it was [Y]

VERDICT: [CASE SOLVED / CASE UNSOLVED]

SCORE: [X]/100
- Suspect: [+40/+0]
- Weapon: [+30/+0]
- Motive: [+30/+0]
- Perfect solve bonus: [+10/+0]
- Efficiency: [+X/-X]

CASE SUMMARY:
[2-3 paragraphs explaining what really happened,
what clues were available, and how the player did]

DETECTIVE RATING: [Novice/Amateur/Competent/Skilled/Master]
==============================================
"""
    return Agent(
        name="Accusation Evaluation Agent",
        role="Judge player accusations and provide case resolution.",
        model=Groq(id=EVALUATOR_MODEL_ID),
        instructions=[instructions],
        markdown=True,
    )


# ============================================================
# GAME ENGINE
# ============================================================

class MurderMysteryGame:
    """Main game engine."""

    def __init__(self):
        self.state = GameState()
        self.conversation_logs: Dict[str, List[Tuple[str, str]]] = {
            sid: [] for sid in SUSPECTS.keys()
        }
        self.current_suspect_id = "s1"

        # Initialize agents
        self.suspect_agents: Dict[str, Agent] = {
            sid: build_suspect_agent(profile) for sid, profile in SUSPECTS.items()
        }
        self.critique_agent = build_critique_agent()
        self.accusation_agent = build_accusation_agent()

    def get_current_suspect(self) -> SuspectProfile:
        return SUSPECTS[self.current_suspect_id]

    def switch_suspect(self, suspect_id: str) -> bool:
        if suspect_id in SUSPECTS:
            self.current_suspect_id = suspect_id
            return True
        return False

    def interrogate(self, player_message: str) -> str:
        """Process a player question and return the suspect's response."""
        profile = self.get_current_suspect()
        suspect_agent = self.suspect_agents[self.current_suspect_id]

        # Get raw response from suspect
        raw_resp = suspect_agent.run(
            f"PLAYER QUESTION:\n{player_message}\n\n"
            "(Remember: you may slip and reveal too much; a separate critique layer will check you.)"
        )
        raw_text = raw_resp.content if hasattr(raw_resp, "content") else str(raw_resp)

        # Critique and revise
        critique_prompt = f"""
You are the critique layer.

PLAYER QUESTION:
{player_message}

SUSPECT PROFILE:
- id: {profile.id}
- name: {profile.name}
- role: {profile.role}
- persona: {profile.persona}
- public_info: {profile.public_info}
- secret_info: {profile.secret_info}
- hard_redlines: {profile.hard_redlines}

CASE TRUTH:
- culprit_id: {CASE_FILE["truth"]["culprit_id"]}
- method: {CASE_FILE["truth"]["method"]}
- motive: {CASE_FILE["truth"]["motive"]}

RAW ANSWER FROM SUSPECT:
\"\"\"{raw_text}\"\"\"

Now output ONLY the final, safe, in-character answer to show the player, after applying your rules.
"""
        crit_resp = self.critique_agent.run(critique_prompt)
        safe_text = crit_resp.content if hasattr(crit_resp, "content") else str(crit_resp)

        # Log the conversation
        self.conversation_logs[self.current_suspect_id].append((player_message, safe_text.strip()))
        self.state.add_turn(self.current_suspect_id)

        return safe_text.strip()

    def make_accusation(self, suspect_id: str, weapon: str, motive: str) -> Tuple[bool, int, str]:
        """Evaluate the player's accusation."""
        truth = CASE_FILE["truth"]

        correct_suspect = (suspect_id == truth["culprit_id"])
        correct_weapon = (weapon.lower().strip() == truth["method"].lower().strip())
        correct_motive = (motive.lower().strip() == truth["motive"].lower().strip())

        # Build transcript summary
        all_transcripts = []
        for sid, logs in self.conversation_logs.items():
            if logs:
                name = SUSPECTS[sid].name
                all_transcripts.append(f"\n--- Interrogation of {name} ({len(logs)} exchanges) ---")
                for i, (q, a) in enumerate(logs[-5:], 1):
                    all_transcripts.append(f"Q{i}: {q}")
                    all_transcripts.append(f"A{i}: {a[:200]}...")

        transcript_text = "\n".join(all_transcripts) if all_transcripts else "No interrogations conducted."

        eval_prompt = f"""
PLAYER'S ACCUSATION:
- Suspect: {suspect_id} ({SUSPECTS[suspect_id].name if suspect_id in SUSPECTS else 'Unknown'})
- Weapon: {weapon}
- Motive: {motive}

THE TRUTH:
- Culprit: {truth["culprit_id"]} ({SUSPECTS[truth["culprit_id"]].name})
- Weapon: {truth["method"]}
- Motive: {truth["motive"]}
- Timeline: {chr(10).join(truth["timeline"])}

CORRECTNESS CHECK:
- Suspect correct: {correct_suspect}
- Weapon correct: {correct_weapon}
- Motive correct: {correct_motive}

GAME STATISTICS:
- Total turns used: {self.state.total_turns}
- Suspects interviewed: {len(self.state.suspects_interviewed)}/3

INTERROGATION HIGHLIGHTS:
{transcript_text}

SUSPECT PROFILES (for context):
- s1: Lydia Blackwood (KILLER) - Elegant heiress, claims she was reading in bedroom
- s2: Dr. Marcus Vale (ACCOMPLICE) - Helped hide the weapon, claims he left at 22:45
- s3: Eleanor Wright (INNOCENT) - Saw Lydia rushing from library at 23:20, too scared to say

Now provide the full CASE RESOLUTION evaluation.
"""
        resp = self.accusation_agent.run(eval_prompt)
        eval_text = resp.content if hasattr(resp, "content") else str(resp)

        # Calculate score
        score = 0
        if correct_suspect:
            score += 40
        if correct_weapon:
            score += 30
        if correct_motive:
            score += 30
        if correct_suspect and correct_weapon and correct_motive:
            score += 10

        if self.state.total_turns <= 10:
            score += 10
        elif self.state.total_turns <= 15:
            score += 5
        elif self.state.total_turns > 20:
            score -= min(20, (self.state.total_turns - 20) * 2)

        score = max(0, min(100, score))

        self.state.accusation_made = True
        self.state.game_won = correct_suspect
        self.state.final_score = score

        return correct_suspect, score, eval_text

    def reset(self):
        """Reset the game for a new playthrough."""
        self.state.reset()
        self.conversation_logs = {sid: [] for sid in SUSPECTS.keys()}
        self.current_suspect_id = "s1"
        # Rebuild agents to clear memory
        self.suspect_agents = {
            sid: build_suspect_agent(profile) for sid, profile in SUSPECTS.items()
        }


# ============================================================
# CLI INTERFACE (for testing)
# ============================================================

def run_cli():
    """Run the game in command-line mode."""
    if not os.environ.get("GROQ_API_KEY"):
        print("Please set GROQ_API_KEY environment variable.")
        print("  export GROQ_API_KEY='your-key-here'")
        return

    game = MurderMysteryGame()

    print("\n" + "=" * 60)
    print("   AI MURDER MYSTERY: THE BLACKWOOD MANSION")
    print("=" * 60)

    v = CASE_FILE["victim"]
    print(f"\nVICTIM: {v['name']}")
    print(f"TIME OF DEATH: {v['time_of_death']}")
    print(f"LOCATION: {v['location']}")
    print(f"CAUSE: {v['cause']}")
    print("\nCommands: /suspect <id>, /suspects, /accuse, /status, /quit")
    print("-" * 60)

    while True:
        suspect = game.get_current_suspect()
        prompt = f"[Turn {game.state.total_turns + 1}/{game.state.max_turns}] [You -> {suspect.name}]: "
        user_input = input(prompt).strip()

        if not user_input:
            continue

        if user_input.lower() in {"/quit", "quit", "exit"}:
            print("Thanks for playing!")
            break

        if user_input.lower() == "/suspects":
            for sid, s in SUSPECTS.items():
                print(f"  {sid} - {s.name}")
            continue

        if user_input.lower() == "/status":
            print(f"Turns: {game.state.total_turns}/{game.state.max_turns}")
            print(f"Interviewed: {list(game.state.suspects_interviewed)}")
            continue

        if user_input.startswith("/suspect "):
            new_id = user_input.split()[1]
            if game.switch_suspect(new_id):
                print(f"Now interrogating: {SUSPECTS[new_id].name}")
            else:
                print(f"Unknown suspect: {new_id}")
            continue

        if user_input.lower() == "/accuse":
            print("\nUsage: /accuse <suspect_id> <weapon> <motive>")
            print("Weapons:", VALID_WEAPONS)
            print("Motives:", VALID_MOTIVES)
            continue

        if user_input.lower().startswith("/accuse "):
            parts = user_input[8:].split(maxsplit=2)
            if len(parts) < 3:
                print("Usage: /accuse <suspect_id> <weapon> <motive>")
                continue
            accused, weapon, motive = parts[0], parts[1], parts[2]
            won, score, text = game.make_accusation(accused, weapon, motive)
            print(text)
            print(f"\n{'CASE SOLVED!' if won else 'CASE UNSOLVED...'} Score: {score}/100")
            break

        # Normal interrogation
        if game.state.total_turns >= game.state.max_turns:
            print("No turns left! Use /accuse to make your accusation.")
            continue

        response = game.interrogate(user_input)
        print(f"\n[{suspect.name}]: {response}\n")


if __name__ == "__main__":
    run_cli()
