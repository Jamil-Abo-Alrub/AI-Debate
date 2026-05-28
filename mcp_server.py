"""MCP server for the Historical Debate League.

Exposes tools that let an LLM client (Claude Code, Claude Desktop, etc.) create
and inspect persona YAML files. The tool is intentionally dumb I/O — the calling
LLM is responsible for generating the persona content (name, era, real quotes,
operational policies). This server just validates against the Persona schema
and writes the file.

Run directly:    python mcp_server.py
Register with Claude Code via .mcp.json (see project root).
"""
from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from core.persona import Persona, write_persona

mcp = FastMCP("debate-personas")


@mcp.tool()
def create_persona(
    name: str,
    era: str,
    anachronism_policy: str,
    debate_stance_hints: str,
    quotes: list[str],
    hard_constraints: Optional[list[str]] = None,
    overwrite: bool = False,
) -> str:
    """Create a persona YAML file for the debate league.

    Guidance for the calling LLM:
    - quotes MUST be real utterances by the figure (or for less-documented
      historical figures, faithful paraphrases of attested writing/speech).
      Provide 5-8 of them. These ground the model's voice — adjective lists
      describing the voice are weaker and should not be used.
    - debate_stance_hints describes the OPERATIONAL posture in a debate:
      what they argue from, what moves they make. Not a bio summary.
    - anachronism_policy resolves how the figure handles events outside
      their lifetime (e.g. "aware of post-1939 concepts but reframes them
      through psychoanalysis").
    - hard_constraints are safety/factual guards (no fabricated quotes
      ).

    Args:
        name: Full name of the figure ("Marie Curie", "Donald Trump").
        era: Lifespan or active period ("1867-1934", "1946-present").
        anachronism_policy: How the figure handles knowledge outside their lifetime.
        debate_stance_hints: Operational debate posture, not bio adjectives.
        quotes: 5-8 real utterances by the figure.
        hard_constraints: Safety/factual rules. Optional.
        overwrite: If true, replaces an existing file with the same slug.

    Returns:
        Path of the written file, or a refusal if the slug already exists.
    """
    persona = Persona(
        name=name,
        era=era,
        anachronism_policy=anachronism_policy,
        debate_stance_hints=debate_stance_hints,
        hard_constraints=hard_constraints or [],
        quotes=quotes,
    )
    try:
        path = write_persona(persona, overwrite=overwrite)
    except FileExistsError as exc:
        return f"Refused: {exc}. Pass overwrite=true to replace, or pick a different name."
    return f"Wrote {path}"


@mcp.tool()
def list_personas() -> list[str]:
    """List slugs of all personas currently available to the debate app."""
    return Persona.list_available()


@mcp.tool()
def get_persona(slug: str) -> dict:
    """Return the full data of one persona by slug.

    Use list_personas() first to see available slugs.
    """
    return Persona.load(slug).model_dump()


if __name__ == "__main__":
    mcp.run()
