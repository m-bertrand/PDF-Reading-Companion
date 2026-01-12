# SkimKnowledge-Automator

> **"The present is big with the future." / "Le présent est gros de l'avenir."** — *G.W. Leibniz*

[English](#en) | [Français](#fr)

---

<a name="en"></a>
## English

Automated tool for extracting, formalizing, and indexing **Skim** annotations (macOS) into **Markdown** files.

### Features
- **NLP Processing**: Lemmatization via Spacy (`fr_core_news_sm`) for standardized tagging.
- **Incremental Workflow**: Only processes new or modified notes.
- **Dry Run Mode**: Test the scan without filesystem modifications.
- **Portability**: Managed through `sys.executable` and `pathlib`.

### Setup
1. **Prerequisites**: macOS and [Skim](https://skim-app.sourceforge.io/).
2. **Dependencies**:
   ```bash
   pip install spacy striprtf biplist
   python -m spacy download fr_core_news_sm
