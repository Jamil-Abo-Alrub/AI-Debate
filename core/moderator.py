import json

from core.debate import Debate
from core.llm import chat

JUDGE_SYSTEM = """You are a neutral debate judge. Score the debate that follows on four axes for EACH debater:
- logic (1-5): coherence and validity of arguments
- evidence (1-5): grounding in facts, examples, real reasoning (not fabricated specifics)
- style (1-5): rhetorical effectiveness
- persona_fidelity (1-5): how authentically they spoke as the historical figure they were portraying

Return STRICT JSON with this exact shape:
{
  "scores": {
    "<debater A name>": {"logic": int, "evidence": int, "style": int, "persona_fidelity": int, "notes": "1-2 sentence rationale"},
    "<debater B name>": {"logic": int, "evidence": int, "style": int, "persona_fidelity": int, "notes": "1-2 sentence rationale"}
  },
  "winner": "<debater name or 'tie'>",
  "rationale": "2-3 sentences explaining the verdict"
}
Output JSON only, no surrounding prose."""


def judge(debate: Debate) -> dict:
    user_msg = (
        f"TOPIC: {debate.topic}\n"
        f"DEBATER A: {debate.persona_a.name}\n"
        f"DEBATER B: {debate.persona_b.name}\n\n"
        f"TRANSCRIPT:\n{debate.transcript_text()}"
    )
    raw = chat(
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    return json.loads(raw)
