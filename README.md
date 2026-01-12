# 📚 SkimKnowledge-Automator

> **"The present is big with the future." / "Le présent est gros de l'avenir."** — *G.W. Leibniz*

[English](#english) | [Français](#français)

---

## English

Transform your PDF annotations into a structured knowledge base. This script automates the extraction, formalization, and indexing of notes taken with the **Skim** app (macOS). It converts binary annotations into Markdown files enriched by NLP for seamless integration into your second brain (**Obsidian**, **Logseq**, etc.).

### ✨ Features
- **NLP Standardization**: Uses lemmatization (Spacy `fr_core_news_sm`) for consistent tagging (e.g., *concepts* -> *concept*).
- **Dry Run Mode**: Test the scan and analysis without writing any files to disk.
- **Robust Dependency Management**: Uses `sys.executable` for full portability.
- **Incremental Workflow**: Only processes new or modified annotations to avoid redundancy.

### 🛠️ Installation & Setup

1. **Prerequisites**: macOS and [Skim](https://skim-app.sourceforge.io/).
2. **Dependencies**:
   ```bash
   pip install spacy striprtf biplist
   python -m spacy download fr_core_news_sm
