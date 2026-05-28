import os

import streamlit as st

try:
    for _key in ("DEEPSEEK_API_KEY",):
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = st.secrets[_key]
except Exception:
    pass  # no secrets configured (e.g. local dev) — fall through to .env

from core.debate import Debate, Phase
from core.i18n import DEFAULT_LANG, LANG_LABELS, SUPPORTED_LANGS, get_lang, phase_label, t
from core.moderator import judge
from core.persona import Persona, write_persona
from core.persona_generator import generate_persona

if "lang" not in st.session_state:
    st.session_state.lang = DEFAULT_LANG

st.set_page_config(page_title=t("page_title"), page_icon="🎤", layout="wide")

st.title(t("title"))
st.caption(t("caption"))

available = Persona.list_available()
if not available:
    st.error(t("no_personas_error"))
    st.stop()


def _render_persona_creator() -> None:
    """Sidebar panel: generate a persona via DeepSeek, edit, save to disk."""
    with st.expander(t("create.expander")):
        new_name = st.text_input(
            t("create.figure_name"),
            key="new_persona_name",
            placeholder=t("create.figure_name_placeholder"),
        )
        new_hint = st.text_area(
            t("create.hint"),
            key="new_persona_hint",
            height=70,
            placeholder=t("create.hint_placeholder"),
        )
        if st.button(t("create.generate"), key="generate_persona"):
            if not new_name.strip():
                st.warning(t("create.name_required"))
            else:
                with st.spinner(t("create.drafting", name=new_name)):
                    try:
                        st.session_state.draft_persona = generate_persona(new_name, new_hint or None)
                    except Exception as exc:
                        st.error(t("create.generation_failed", exc=exc))

        draft = st.session_state.get("draft_persona")
        if draft is None:
            return

        st.markdown(t("create.preview"))
        with st.form("edit_persona_form"):
            d_name = st.text_input(t("create.field_name"), value=draft.name)
            d_era = st.text_input(t("create.field_era"), value=draft.era)
            d_policy = st.text_area(t("create.field_anachronism"), value=draft.anachronism_policy, height=70)
            d_stance = st.text_area(t("create.field_stance"), value=draft.debate_stance_hints, height=80)
            d_constraints = st.text_area(
                t("create.field_constraints"),
                value="\n".join(draft.hard_constraints),
                height=100,
            )
            d_quotes = st.text_area(
                t("create.field_quotes"),
                value="\n".join(draft.quotes),
                height=200,
            )
            overwrite = st.checkbox(t("create.overwrite"), value=False)

            cols = st.columns(2)
            save = cols[0].form_submit_button(t("create.save"), type="primary")
            cancel = cols[1].form_submit_button(t("create.cancel"))

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
                st.error(t("create.file_exists", exc=exc))
            except Exception as exc:
                st.error(t("create.save_failed", exc=exc))
            else:
                st.session_state.pop("draft_persona", None)
                st.success(t("create.saved", filename=path.name))
                st.rerun()


with st.sidebar:
    current_lang = st.session_state.lang
    lang_choice = st.selectbox(
        t("sidebar.language"),
        options=list(SUPPORTED_LANGS),
        index=list(SUPPORTED_LANGS).index(current_lang),
        format_func=lambda code: LANG_LABELS[code],
        key="lang_selector",
    )
    if lang_choice != current_lang:
        st.session_state.lang = lang_choice
        st.rerun()

    st.divider()
    st.header(t("sidebar.setup"))
    a_slug = st.selectbox(t("sidebar.debater_a"), available, index=0, key="a_slug")
    default_b_index = 1 if len(available) > 1 else 0
    b_slug = st.selectbox(t("sidebar.debater_b"), available, index=default_b_index, key="b_slug")
    topic = st.text_input(t("sidebar.topic"), value=t("sidebar.topic_default"), key="topic_input")
    same_persona = a_slug == b_slug
    if same_persona:
        st.warning(t("sidebar.same_persona_warning"))
    start = st.button(t("sidebar.start_debate"), type="primary", disabled=same_persona)
    if st.button(t("sidebar.reset")):
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
        language=get_lang(),
    )
    st.session_state.verdict = None

if "debate" not in st.session_state:
    st.info(t("main.welcome"))
    st.stop()

debate: Debate = st.session_state.debate

st.subheader(f"📜 {debate.topic}")
st.markdown(f"**{debate.persona_a.name}**{t('main.vs')}**{debate.persona_b.name}**")
st.divider()

for turn in debate.turns:
    with st.chat_message(turn.speaker):
        st.markdown(f"**{turn.speaker}** — *{phase_label(turn.phase)}*")
        st.markdown(turn.content)

if not debate.is_done and debate.current_phase != Phase.VERDICT:
    speaker = debate.speaker_for(debate.current_phase)
    with st.chat_message(speaker.name):
        st.markdown(f"**{speaker.name}** — *{phase_label(debate.current_phase)}*")
        try:
            content = st.write_stream(debate.stream_next_turn())
        except Exception as exc:
            st.error(t("main.llm_failed", exc=exc))
            st.stop()
    debate.record_turn(content)
    st.rerun()

if debate.current_phase == Phase.VERDICT and st.session_state.get("verdict") is None:
    with st.spinner(t("main.judge_deliberating")):
        try:
            st.session_state.verdict = judge(debate)
        except Exception as exc:
            st.error(t("main.judge_failed", exc=exc))
            st.stop()
    debate.advance_to_done()
    st.rerun()

verdict = st.session_state.get("verdict")
if verdict:
    st.divider()
    st.subheader(f"⚖️ {t('verdict.title')}")

    scores = verdict.get("scores", {})
    col_a, col_b = st.columns(2)
    for col, persona in [(col_a, debate.persona_a), (col_b, debate.persona_b)]:
        s = scores.get(persona.name, {})
        with col:
            st.markdown(f"### {persona.name}")
            for axis in ("logic", "evidence", "style", "persona_fidelity"):
                if axis in s:
                    st.metric(t(f"metric.{axis}"), f"{s[axis]}/5")
            if s.get("notes"):
                st.caption(s["notes"])

    winner = verdict.get("winner")
    if winner == "tie":
        winner = t("verdict.tie")
    st.markdown(f"**{t('verdict.winner')}:** {winner or '—'}")
    if verdict.get("rationale"):
        st.markdown(f"*{verdict['rationale']}*")
