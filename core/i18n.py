"""Minimal i18n for the Debate League.

One flat dict per language. UI uses t(key); LLM-facing directives use
LANG_DIRECTIVES so debate output matches the user's chosen language.
"""
from typing import Optional

import streamlit as st

DEFAULT_LANG = "fr"
SUPPORTED_LANGS = ("fr", "en")
LANG_LABELS = {"fr": "Français", "en": "English"}


LANG_DIRECTIVES = {
    "en": "Write your response entirely in English.",
    "fr": "Rédige ta réponse entièrement en français.",
}


JUDGE_LANG_DIRECTIVES = {
    "en": "All free-text fields in the JSON ('notes', 'rationale') must be written in English.",
    "fr": "Tous les champs textuels libres du JSON (« notes », « rationale ») doivent être rédigés en français.",
}


TRANSLATIONS = {
    "fr": {
        # page
        "page_title": "Ligue de Débat",
        "title": "Ligue de Débat des Figures Historiques & Célèbres",
        "caption": (
            "Satire et usage éducatif uniquement. Tous les propos sont générés "
            "par IA et ne représentent pas les opinions réelles des personnes "
            "représentées."
        ),
        "no_personas_error": "Aucun personnage trouvé dans personas/. Ajoutez au moins un fichier YAML.",
        # sidebar — setup
        "sidebar.language": "Langue",
        "sidebar.setup": "Configuration",
        "sidebar.debater_a": "Débatteur A",
        "sidebar.debater_b": "Débatteur B",
        "sidebar.topic": "Sujet",
        "sidebar.topic_default": "Les réseaux sociaux doivent-ils être régulés par les gouvernements ?",
        "sidebar.same_persona_warning": "Choisissez deux débatteurs différents.",
        "sidebar.start_debate": "Lancer le débat",
        "sidebar.reset": "Réinitialiser",
        # sidebar — create persona
        "create.expander": "➕ Créer un nouveau débatteur",
        "create.figure_name": "Nom de la figure",
        "create.figure_name_placeholder": "ex. Marie Curie",
        "create.hint": "Indice facultatif",
        "create.hint_placeholder": "ex. axée sur la rigueur expérimentale",
        "create.generate": "Générer",
        "create.name_required": "Entrez d'abord un nom.",
        "create.drafting": "Génération de {name}…",
        "create.generation_failed": "Échec de la génération : {exc}",
        "create.preview": "**Aperçu — modifiez avant d'enregistrer :**",
        "create.field_name": "Nom",
        "create.field_era": "Époque",
        "create.field_anachronism": "Politique d'anachronisme",
        "create.field_stance": "Posture de débat",
        "create.field_constraints": "Contraintes strictes (une par ligne)",
        "create.field_quotes": "Citations (une par ligne)",
        "create.overwrite": "Écraser si un personnage de ce nom existe déjà",
        "create.save": "Enregistrer",
        "create.cancel": "Annuler",
        "create.file_exists": "{exc}. Cochez « Écraser » pour remplacer.",
        "create.save_failed": "Échec de l'enregistrement : {exc}",
        "create.saved": "Enregistré : {filename}",
        # main view
        "main.welcome": "Choisissez deux débatteurs et un sujet dans la barre latérale, puis cliquez sur **Lancer le débat**.",
        "main.vs": "  contre  ",
        "main.llm_failed": "Échec de l'appel au LLM : {exc}",
        "main.judge_deliberating": "Le juge délibère…",
        "main.judge_failed": "Échec de l'appel au juge : {exc}",
        # verdict
        "verdict.title": "Verdict",
        "verdict.winner": "Vainqueur",
        "verdict.tie": "égalité",
        "metric.logic": "Logique",
        "metric.evidence": "Preuves",
        "metric.style": "Style",
        "metric.persona_fidelity": "Fidélité au personnage",
        # phases
        "phase.opening": "Ouverture",
        "phase.rebuttal": "Réfutation",
        "phase.closing": "Conclusion",
        "phase.verdict": "Verdict",
    },
    "en": {
        # page
        "page_title": "Debate League",
        "title": "Historical & Celebrity Figures Debate League",
        "caption": (
            "Satire and educational use only. All statements are AI-generated "
            "and do not represent the real views of any person depicted."
        ),
        "no_personas_error": "No personas found in personas/. Add at least one YAML file.",
        # sidebar — setup
        "sidebar.language": "Language",
        "sidebar.setup": "Setup",
        "sidebar.debater_a": "Debater A",
        "sidebar.debater_b": "Debater B",
        "sidebar.topic": "Topic",
        "sidebar.topic_default": "Should social media be regulated by governments?",
        "sidebar.same_persona_warning": "Pick two different debaters.",
        "sidebar.start_debate": "Start debate",
        "sidebar.reset": "Reset",
        # sidebar — create persona
        "create.expander": "➕ Create new debater",
        "create.figure_name": "Figure's name",
        "create.figure_name_placeholder": "e.g. Marie Curie",
        "create.hint": "Optional hint",
        "create.hint_placeholder": "e.g. focus on her radioactivity work and empirical mindset",
        "create.generate": "Generate",
        "create.name_required": "Enter a name first.",
        "create.drafting": "Drafting {name}…",
        "create.generation_failed": "Generation failed: {exc}",
        "create.preview": "**Preview — edit before saving:**",
        "create.field_name": "Name",
        "create.field_era": "Era",
        "create.field_anachronism": "Anachronism policy",
        "create.field_stance": "Debate stance hints",
        "create.field_constraints": "Hard constraints (one per line)",
        "create.field_quotes": "Quotes (one per line)",
        "create.overwrite": "Overwrite if a persona with this name already exists",
        "create.save": "Save",
        "create.cancel": "Cancel",
        "create.file_exists": "{exc}. Tick 'Overwrite' to replace.",
        "create.save_failed": "Save failed: {exc}",
        "create.saved": "Saved {filename}",
        # main view
        "main.welcome": "Pick two debaters and a topic in the sidebar, then click **Start debate**.",
        "main.vs": "  vs  ",
        "main.llm_failed": "LLM call failed: {exc}",
        "main.judge_deliberating": "Judge deliberating…",
        "main.judge_failed": "Judge call failed: {exc}",
        # verdict
        "verdict.title": "Verdict",
        "verdict.winner": "Winner",
        "verdict.tie": "tie",
        "metric.logic": "Logic",
        "metric.evidence": "Evidence",
        "metric.style": "Style",
        "metric.persona_fidelity": "Persona Fidelity",
        # phases
        "phase.opening": "Opening",
        "phase.rebuttal": "Rebuttal",
        "phase.closing": "Closing",
        "phase.verdict": "Verdict",
    },
}


def get_lang() -> str:
    return st.session_state.get("lang", DEFAULT_LANG)


def t(key: str, **kwargs) -> str:
    """Look up a translation. Falls back to the key itself if missing."""
    lang = get_lang()
    text = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG]).get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANG].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def phase_label(phase) -> str:
    """Translate a Phase enum value to a localized label."""
    name = phase.value
    if name.startswith("opening"):
        return t("phase.opening")
    if name.startswith("rebuttal"):
        return t("phase.rebuttal")
    if name.startswith("closing"):
        return t("phase.closing")
    return t(f"phase.{name}")


def debate_directive(lang: Optional[str] = None) -> str:
    return LANG_DIRECTIVES[lang or get_lang()]


def judge_directive(lang: Optional[str] = None) -> str:
    return JUDGE_LANG_DIRECTIVES[lang or get_lang()]
