from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterator, List, Optional

from core.llm import stream_chat
from core.persona import Persona


class Phase(str, Enum):
    OPENING_A = "opening_a"
    OPENING_B = "opening_b"
    REBUTTAL_A = "rebuttal_a"
    REBUTTAL_B = "rebuttal_b"
    CLOSING_A = "closing_a"
    CLOSING_B = "closing_b"
    VERDICT = "verdict"
    DONE = "done"


PHASE_ORDER: List[Phase] = [
    Phase.OPENING_A, Phase.OPENING_B,
    Phase.REBUTTAL_A, Phase.REBUTTAL_B,
    Phase.CLOSING_A, Phase.CLOSING_B,
    Phase.VERDICT,
]


PHASE_INSTRUCTIONS: Dict[Phase, str] = {
    Phase.OPENING_A: "Give your opening statement on the topic. Around 150 words. Stake out your position clearly.",
    Phase.OPENING_B: "Give your opening statement on the topic. Around 150 words. Stake out your position; you may briefly reference your opponent's opening.",
    Phase.REBUTTAL_A: "Rebut your opponent's opening directly. Around 150 words. Attack the strongest part of their argument, not the weakest.",
    Phase.REBUTTAL_B: "Rebut your opponent's most recent argument directly. Around 150 words.",
    Phase.CLOSING_A: "Closing statement, around 120 words. Introduce no new arguments — drive home why your position has prevailed.",
    Phase.CLOSING_B: "Closing statement, around 120 words. Drive home your case.",
}


PHASE_LABEL: Dict[Phase, str] = {
    Phase.OPENING_A: "Opening",
    Phase.OPENING_B: "Opening",
    Phase.REBUTTAL_A: "Rebuttal",
    Phase.REBUTTAL_B: "Rebuttal",
    Phase.CLOSING_A: "Closing",
    Phase.CLOSING_B: "Closing",
    Phase.VERDICT: "Verdict",
}


@dataclass
class Turn:
    phase: Phase
    speaker: str
    content: str


@dataclass
class Debate:
    persona_a: Persona
    persona_b: Persona
    topic: str
    turns: List[Turn] = field(default_factory=list)
    current_phase_index: int = 0

    @property
    def current_phase(self) -> Phase:
        if self.current_phase_index >= len(PHASE_ORDER):
            return Phase.DONE
        return PHASE_ORDER[self.current_phase_index]

    @property
    def is_done(self) -> bool:
        return self.current_phase == Phase.DONE

    def speaker_for(self, phase: Phase) -> Optional[Persona]:
        if phase in (Phase.OPENING_A, Phase.REBUTTAL_A, Phase.CLOSING_A):
            return self.persona_a
        if phase in (Phase.OPENING_B, Phase.REBUTTAL_B, Phase.CLOSING_B):
            return self.persona_b
        return None

    def transcript_text(self) -> str:
        if not self.turns:
            return "(no turns yet — you are speaking first)"
        return "\n\n".join(f"{t.speaker}: {t.content}" for t in self.turns)

    def stream_next_turn(self) -> Iterator[str]:
        phase = self.current_phase
        speaker = self.speaker_for(phase)
        if speaker is None:
            return iter(())

        opponent = self.persona_b if speaker is self.persona_a else self.persona_a
        instruction = PHASE_INSTRUCTIONS[phase]
        user_msg = (
            f"DEBATE TOPIC: {self.topic}\n"
            f"YOUR OPPONENT: {opponent.name}\n\n"
            f"TRANSCRIPT SO FAR:\n{self.transcript_text()}\n\n"
            f"YOUR TASK: {instruction}"
        )

        messages = [
            {"role": "system", "content": speaker.system_prompt()},
            {"role": "user", "content": user_msg},
        ]
        yield from stream_chat(messages, temperature=0.85)

    def record_turn(self, content: str) -> None:
        phase = self.current_phase
        speaker = self.speaker_for(phase)
        if speaker is None:
            return
        self.turns.append(Turn(phase=phase, speaker=speaker.name, content=content))
        self.current_phase_index += 1

    def advance_to_done(self) -> None:
        self.current_phase_index = len(PHASE_ORDER)
