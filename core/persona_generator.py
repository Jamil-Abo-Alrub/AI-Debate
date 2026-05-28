"""Generate persona YAML content from a figure's name using DeepSeek.

Used by the Streamlit UI's "Create persona" panel. The MCP server does NOT
use this — when the calling client is itself an LLM, that client generates
the content directly and the MCP tool only writes.
"""
import json
from typing import Optional

from core.llm import chat
from core.persona import Persona

GENERATOR_SYSTEM = """You are a curator for a Historical & Celebrity Debate League app.

Your job: produce a persona spec for the figure the user names. The spec is consumed
by an LLM that will play the figure in structured debates. Therefore the spec must
STEER the LLM, not describe the figure to a human reader.

DESIGN PRINCIPLES (important):
- The LLM playing the figure already has rich latent knowledge of famous people from its
  training data. Do NOT write adjective lists describing how they sound — that flattens
  their voice. Lean on real quotes instead.
- Quotes are the most important field. They ground the LLM's voice in actual utterances.
  Provide 5-8 REAL quotes (writings, speeches, interviews, attested statements). For
  poorly-documented historical figures, faithful paraphrases of attested writing are
  acceptable, but mark them as such mentally — never invent a memorable quote.
- debate_stance_hints describes the OPERATIONAL posture: what arguments they reach for,
  what rhetorical moves they make, what they prize. Not a bio summary, not "speaks in
  short sentences."
- anachronism_policy resolves how the figure handles events outside their lifetime.
  One sentence describing their reasoning style when faced with modern topics.
- hard_constraints are safety / factual guards (no fabricated quotes attributed to real
  living individuals, no medical advice for medical figures, no battle inventions for
  generals, etc.). 2-4 items.

OUTPUT FORMAT — respond with JSON ONLY, no surrounding prose, matching this schema:
{
  "name": "<full name as commonly known>",
  "era": "<lifespan or active period, e.g. '1867-1934' or '1946-present'>",
  "anachronism_policy": "<one sentence>",
  "debate_stance_hints": "<one or two sentences on operational debate posture>",
  "hard_constraints": ["<rule>", "<rule>", ...],
  "quotes": ["<real quote>", "<real quote>", ...]
}"""


def generate_persona(name: str, hint: Optional[str] = None) -> Persona:
    """Ask DeepSeek to draft a Persona for a named figure.

    Returns a validated Persona instance. The caller (the Streamlit UI) typically
    shows this as an editable form before saving.
    """
    user_msg = f"Generate the persona spec for: {name}"
    if hint and hint.strip():
        user_msg += f"\n\nUser hint: {hint.strip()}"

    raw = chat(
        messages=[
            {"role": "system", "content": GENERATOR_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.5,
        response_format={"type": "json_object"},
    )
    data = json.loads(raw)
    return Persona(**data)
