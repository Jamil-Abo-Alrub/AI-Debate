import os
from pathlib import Path

import streamlit as st

_SECRETS_PATHS = [
    Path.home() / ".streamlit" / "secrets.toml",
    Path(".streamlit") / "secrets.toml",
]
if any(p.exists() for p in _SECRETS_PATHS):
    for _key in ("DEEPSEEK_API_KEY",):
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = st.secrets[_key]

from core.debate import Debate, Phase, PHASE_LABEL
from core.moderator import judge
from core.persona import Persona, write_persona
from core.persona_generator import generate_persona

st.set_page_config(page_title="Historical Debate League", page_icon="🎤", layout="wide")

st.title("Historical & Celebrity Debate League")
st.caption(
    "Satire and educational use only. All statements are AI-generated and do not "
    "represent the real views of any person depicted."
)

available = Persona.list_available()
if not available:
    st.error("No personas found in personas/. Add at least one YAML file.")
    st.stop()

def _render_persona_creator() -> None:
    """Sidebar panel: generate a persona via DeepSeek, edit, save to disk."""
    with st.expander("➕ Create new debater"):
        new_name = st.text_input("Figure's name", key="new_persona_name", placeholder="e.g. Marie Curie")
        new_hint = st.text_area(
            "Optional hint",
            key="new_persona_hint",
            height=70,
            placeholder="e.g. focus on her radioactivity work and empirical mindset",
        )
        if st.button("Generate", key="generate_persona"):
            if not new_name.strip():
                st.warning("Enter a name first.")
            else:
                with st.spinner(f"Drafting {new_name}…"):
                    try:
                        st.session_state.draft_persona = generate_persona(new_name, new_hint or None)
                    except Exception as exc:
                        st.error(f"Generation failed: {exc}")

        draft = st.session_state.get("draft_persona")
        if draft is None:
            return

        st.markdown("**Preview — edit before saving:**")
        with st.form("edit_persona_form"):
            d_name = st.text_input("Name", value=draft.name)
            d_era = st.text_input("Era", value=draft.era)
            d_policy = st.text_area("Anachronism policy", value=draft.anachronism_policy, height=70)
            d_stance = st.text_area("Debate stance hints", value=draft.debate_stance_hints, height=80)
            d_constraints = st.text_area(
                "Hard constraints (one per line)",
                value="\n".join(draft.hard_constraints),
                height=100,
            )
            d_quotes = st.text_area(
                "Quotes (one per line)",
                value="\n".join(draft.quotes),
                height=200,
            )
            overwrite = st.checkbox("Overwrite if a persona with this name already exists", value=False)

            cols = st.columns(2)
            save = cols[0].form_submit_button("Save", type="primary")
            cancel = cols[1].form_submit_button("Cancel")

        if cancel:
            st.session_state.pop("draft_persona", None)
            st.rerun()
        if save:
            try:
                final = Persona(
                    name=d_name.strip(),
                    era=d_era.strip(),
                    anachronism_policy=d_policy.strip(),
                    debate_stance_hints=d_stance.strip(),
                    hard_constraints=[ln.strip() for ln in d_constraints.splitlines() if ln.strip()],
                    quotes=[ln.strip() for ln in d_quotes.splitlines() if ln.strip()],
                )
                path = write_persona(final, overwrite=overwrite)
            except FileExistsError as exc:
                st.error(f"{exc}. Tick 'Overwrite' to replace.")
            except Exception as exc:
                st.error(f"Save failed: {exc}")
            else:
                st.session_state.pop("draft_persona", None)
                st.success(f"Saved {path.name}")
                st.rerun()


with st.sidebar:
    st.header("Setup")
    a_slug = st.selectbox("Debater A", available, index=0, key="a_slug")
    default_b_index = 1 if len(available) > 1 else 0
    b_slug = st.selectbox("Debater B", available, index=default_b_index, key="b_slug")
    topic = st.text_input("Topic", value="Should social media be regulated by governments?")
    same_persona = a_slug == b_slug
    if same_persona:
        st.warning("Pick two different debaters.")
    start = st.button("Start debate", type="primary", disabled=same_persona)
    if st.button("Reset"):
        for k in ("debate", "verdict"):
            st.session_state.pop(k, None)
        st.rerun()
    st.divider()
    _render_persona_creator()

if start:
    st.session_state.debate = Debate(
        persona_a=Persona.load(a_slug),
        persona_b=Persona.load(b_slug),
        topic=topic,
    )
    st.session_state.verdict = None

if "debate" not in st.session_state:
    st.info("Pick two debaters and a topic in the sidebar, then click **Start debate**.")
    st.stop()

debate: Debate = st.session_state.debate

st.subheader(f"📜 {debate.topic}")
st.markdown(f"**{debate.persona_a.name}**  vs  **{debate.persona_b.name}**")
st.divider()

for turn in debate.turns:
    with st.chat_message(turn.speaker):
        st.markdown(f"**{turn.speaker}** — *{PHASE_LABEL[turn.phase]}*")
        st.markdown(turn.content)

if not debate.is_done and debate.current_phase != Phase.VERDICT:
    speaker = debate.speaker_for(debate.current_phase)
    with st.chat_message(speaker.name):
        st.markdown(f"**{speaker.name}** — *{PHASE_LABEL[debate.current_phase]}*")
        try:
            content = st.write_stream(debate.stream_next_turn())
        except Exception as exc:
            st.error(f"LLM call failed: {exc}")
            st.stop()
    debate.record_turn(content)
    st.rerun()

if debate.current_phase == Phase.VERDICT and st.session_state.get("verdict") is None:
    with st.spinner("Judge deliberating..."):
        try:
            st.session_state.verdict = judge(debate)
        except Exception as exc:
            st.error(f"Judge call failed: {exc}")
            st.stop()
    debate.advance_to_done()
    st.rerun()

verdict = st.session_state.get("verdict")
if verdict:
    st.divider()
    st.subheader("⚖️ Verdict")

    scores = verdict.get("scores", {})
    col_a, col_b = st.columns(2)
    for col, persona in [(col_a, debate.persona_a), (col_b, debate.persona_b)]:
        s = scores.get(persona.name, {})
        with col:
            st.markdown(f"### {persona.name}")
            for axis in ("logic", "evidence", "style", "persona_fidelity"):
                if axis in s:
                    st.metric(axis.replace("_", " ").title(), f"{s[axis]}/5")
            if s.get("notes"):
                st.caption(s["notes"])

    winner = verdict.get("winner", "—")
    st.markdown(f"**Winner:** {winner}")
    if verdict.get("rationale"):
        st.markdown(f"*{verdict['rationale']}*")
