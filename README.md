# Historical & Celebrity Figures Debate League

Une application web qui met en scène des débats structurés entre figures historiques et personnalités célèbres, générés par un LLM. L'utilisateur choisit deux personnages, propose un sujet, et regarde le débat se dérouler en temps réel — avec un juge qui note chaque débatteur et désigne un vainqueur.

> **Avertissement.** Tous les propos sont générés par IA à des fins éducatives et satiriques. Ils ne représentent en aucun cas les opinions réelles des personnes représentées.

---

## Fonctionnalités

- **Débats structurés en six tours** : ouverture, réfutation, conclusion pour chaque débatteur.
- **Streaming token-par-token** : les réponses s'affichent en direct, sans temps mort.
- **Juge automatique** : évalue chaque débatteur sur quatre axes (logique, preuves, style, fidélité au personnage) et désigne un vainqueur.
- **Création de personnages depuis l'interface** : on entre un nom (par ex. *Marie Curie*), DeepSeek génère une fiche de persona qu'on peut éditer avant de la sauvegarder.
- **Serveur MCP** intégré pour créer des personnages depuis Claude Code, Claude Desktop ou tout client compatible MCP.

---

## Philosophie de conception

L'enjeu principal n'est pas l'orchestration ni l'UI — c'est la **fidélité au personnage**. La plupart des démonstrations « débat de célébrités » échouent parce qu'elles se limitent à des prompts du type *« comporte-toi comme X »*, produisant des caricatures plates.

Notre approche repose sur trois principes :

1. **Les YAMLs de personnages ne décrivent pas la voix — ils l'ancrent.** Pas de listes d'adjectifs (« parle de façon clinique et analytique »). À la place, 5 à 8 vraies citations du personnage. Le modèle s'aligne sur de vraies paroles plutôt que sur un résumé de celles-ci.
2. **Une machine à états pour le débat, pas du chat libre.** Chaque phase (ouverture, réfutation, conclusion) a ses propres instructions et contraintes de longueur. Cela empêche la dérive et produit une structure regardable.
3. **Le juge est un agent séparé.** Sortie JSON structurée. Décorrèle l'évaluation de la génération.

---

## Architecture

```
debate-project/
├── app.py                       # Interface Streamlit (mince)
├── mcp_server.py                # Serveur MCP pour clients LLM externes
├── .mcp.json                    # Configuration MCP auto-découvrable
│
├── core/
│   ├── llm.py                   # Client DeepSeek (SDK OpenAI + base_url)
│   ├── persona.py               # Modèle Pydantic + lecture/écriture YAML
│   ├── persona_generator.py     # Génération d'un personnage via DeepSeek
│   ├── debate.py                # Machine à états du débat
│   └── moderator.py             # Agent juge (sortie JSON structurée)
│
├── personas/                    # Bibliothèque de personnages
│   ├── trump.yaml
│   ├── freud.yaml
│   └── napoleon.yaml
│
├── requirements.txt
├── runtime.txt                  # Version de Python (pour Streamlit Cloud)
├── .streamlit/config.toml
└── .env.example
```

---

## Stack technique

| Composant | Choix |
|---|---|
| LLM | DeepSeek (API compatible OpenAI) |
| UI | Streamlit |
| Schéma de personnages | Pydantic v2 |
| Stockage des personnages | Fichiers YAML |
| Protocole de tooling externe | MCP (Model Context Protocol) |
| Déploiement | Streamlit Community Cloud |

---

## Installation locale

Prérequis : **Python 3.10 ou supérieur**.

```bash
# 1. Cloner le dépôt
git clone https://github.com/Jamil-Abo-Alrub/debate-project.git
cd debate-project

# 2. Créer un environnement virtuel
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer la clé API
cp .env.example .env
# Éditer .env et coller votre clé DeepSeek
```

### Obtenir une clé DeepSeek

Créer un compte sur [platform.deepseek.com](https://platform.deepseek.com/), générer une clé API, et la coller dans `.env` :

```
DEEPSEEK_API_KEY=sk-votre-cle-ici
```

### Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`.

---

## Utilisation

### Lancer un débat

1. Dans la barre latérale, choisir deux débatteurs différents (par ex. *Trump* vs *Freud*).
2. Saisir un sujet (par ex. *« Faut-il réguler les réseaux sociaux ? »*).
3. Cliquer sur **Start debate**.
4. Les six tours s'enchaînent automatiquement avec streaming.
5. Le juge délibère et affiche le verdict.

### Créer un nouveau débatteur depuis l'interface

1. Déplier le panneau **➕ Create new debater** dans la barre latérale.
2. Entrer le nom complet (par ex. *Marie Curie*).
3. Optionnel : ajouter un indice (par ex. *« axée sur la rigueur expérimentale »*).
4. Cliquer sur **Generate**. DeepSeek produit une fiche complète (ère, citations, posture de débat, contraintes).
5. **Éditer le brouillon** avant de sauvegarder — les LLMs inventent parfois des citations qui semblent réelles ; vérifier les citations est important.
6. Cliquer sur **Save**. Le fichier YAML apparaît dans `personas/` et devient immédiatement disponible dans les listes déroulantes.

---

## Serveur MCP (optionnel)

Le serveur MCP expose trois outils (`create_persona`, `list_personas`, `get_persona`) à un client LLM local comme **Claude Code** ou **Claude Desktop**. Cela permet de créer des personnages en conversant avec son assistant IA plutôt que par l'interface web.

### Enregistrement automatique avec Claude Code

Le fichier [`.mcp.json`](.mcp.json) déclare le serveur. Au démarrage de Claude Code dans ce dossier, le serveur est détecté automatiquement. Vérifier avec :

```
/mcp
```

### Exemple d'utilisation

Dans une session Claude Code, dans ce dossier :

> *Crée un débatteur Marie Curie pour mon application : trouve 6 vraies citations issues de ses écrits, et donne-lui une posture ancrée dans l'empirisme.*

Claude appellera `create_persona` avec les bons arguments, et `personas/marie_curie.yaml` apparaîtra.

> **Note.** Le serveur MCP est un outil de développeur local — il ne fait pas partie du déploiement web. Les utilisateurs de l'application Streamlit créent leurs personnages depuis l'interface, qui appelle directement DeepSeek.

---

## Schéma d'un personnage

Chaque persona YAML suit le schéma défini dans [`core/persona.py`](core/persona.py) :

```yaml
name: Sigmund Freud
era: 1856-1939
anachronism_policy: >
  conscient des concepts postérieurs à 1939 mais les reformule à travers
  la théorie psychanalytique de son époque
debate_stance_hints: >
  regarde au-delà des arguments de surface pour identifier les motivations
  inconscientes et les pulsions de l'adversaire
hard_constraints:
  - ne pas inventer d'événements datés postérieurs à 1939
  - ne pas donner de conseils médicaux ou pharmacologiques modernes
quotes:
  - "La voix de l'intellect est faible, mais elle ne se repose pas avant d'avoir été entendue."
  - "Là où ça était, le moi doit advenir."
  # ... 4 à 6 citations supplémentaires
```

**Règle importante.** Les `quotes` doivent être de vraies paroles attestées du personnage (écrits, discours, déclarations publiques). Pour les figures peu documentées, des paraphrases fidèles d'écrits attestés sont acceptables — mais ne jamais inventer une citation marquante.

---

