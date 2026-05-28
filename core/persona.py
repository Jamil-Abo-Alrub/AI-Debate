import re
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field

PERSONAS_DIR = Path(__file__).resolve().parent.parent / "personas"


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "_", s)
    return s or "persona"


def write_persona(persona: "Persona", overwrite: bool = False) -> Path:
    """Write a persona to disk. Returns the path written.

    Raises FileExistsError if the slug exists and overwrite=False.
    """
    slug = slugify(persona.name)
    path = PERSONAS_DIR / f"{slug}.yaml"
    if path.exists() and not overwrite:
        raise FileExistsError(f"Persona '{slug}' already exists at {path}")
    PERSONAS_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            persona.model_dump(),
            f,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=120,
        )
    return path


class Persona(BaseModel):
    name: str
    era: str
    anachronism_policy: str = ""
    debate_stance_hints: str = ""
    hard_constraints: List[str] = Field(default_factory=list)
    quotes: List[str] = Field(default_factory=list)

    @classmethod
    def load(cls, slug: str) -> "Persona":
        path = PERSONAS_DIR / f"{slug}.yaml"
        with open(path, "r", encoding="utf-8") as f:
            return cls(**yaml.safe_load(f))

    @classmethod
    def list_available(cls) -> List[str]:
        return sorted(p.stem for p in PERSONAS_DIR.glob("*.yaml"))

    def system_prompt(self) -> str:
        quotes_block = "\n\n".join(f'"{q}"' for q in self.quotes) or "(no quotes provided)"
        constraints = "\n".join(f"- {c}" for c in self.hard_constraints)
        return f"""You are {self.name} ({self.era}).

Speak in your authentic voice. Below are real things you have written or said — match this voice, do not summarize or describe it:

{quotes_block}

Anachronism policy: {self.anachronism_policy}

Debate posture: {self.debate_stance_hints}

Hard rules:
{constraints}
- Stay in character at all times. Never break the fourth wall.
- Do not narrate stage directions, do not refer to yourself in the third person.
- Respond directly to the most recent argument from your opponent when one exists.
- Do not fabricate specific quotes or statistics. 
"""