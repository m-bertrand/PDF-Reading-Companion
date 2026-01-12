# 📚 SkimKnowledge-Automator

> "The present is big with the future." / "Le présent est gros de l'avenir." — G.W. Leibniz

[English](#english) | [Français](#français)

---

## English

Transform your PDF annotations into a structured knowledge base. This script automates the extraction, formalization, and indexing of notes taken with the Skim app (macOS). It converts binary annotations into Markdown files enriched by NLP for seamless integration into your second brain (Obsidian, Logseq, etc.).

### Features

*   **NLP Standardization**: Uses lemmatization (Spacy `fr_core_news_sm`) for consistent tagging (e.g., *concepts* → *concept*).
*   **Dry Run Mode**: Test the scan and analysis without writing any files to disk.
*   **Robust Dependency Management**: Uses `sys.executable` for full portability.
*   **Incremental Workflow**: Only processes new or modified annotations to avoid redundancy.

### Installation & Setup

**Prerequisites**: macOS and the [Skim PDF reader](https://skim-app.sourceforge.io/).

**Install Dependencies**:

```bash
pip install spacy striprtf biplist
python -m spacy download fr_core_news_sm
```

**Configuration**: Open `organize_notes.py` and define your personal paths in the **CONFIGURATION** section:

*   `WATCHED_SUBFOLDERS`: Names of the folders to scan (within your Downloads by default).
*   `DEST_DIR`: Where you want your structured Markdown notes to land.

### Usage

Run the script manually or via a scheduled task (Cron or Automator):

```bash
# Standard run
python organize_notes.py

# Simulation run (no files written)
python organize_notes.py --dry-run
```

---

## Français

Transformez vos annotations PDF en une base de connaissances structurée. Ce script automatise l'extraction, la formalisation et l'indexation des notes prises avec l'application Skim (macOS). Il convertit vos annotations binaires en fichiers Markdown enrichis par NLP pour une intégration fluide dans votre "second cerveau" (Obsidian, Logseq, etc.).

### Fonctions Clés

*   **Standardisation NLP** : Utilisation de la lemmatisation pour des tags cohérents (ex: *concepts* → *concept*).
*   **Mode Dry Run** : Testez le scan et l'analyse sans écriture sur le disque.
*   **Gestion Robuste** : Utilisation de `sys.executable` pour une portabilité totale entre environnements.
*   **Workflow Incrémental** : Ne traite que les nouveautés ou modifications depuis le dernier tri.

### Configuration & Installation

**Prérequis** : macOS et le lecteur PDF [Skim](https://skim-app.sourceforge.io/).

**Installation** :

```bash
pip install spacy striprtf biplist
python -m spacy download fr_core_news_sm
```

**Paramétrage** : Modifiez les variables dans la section **CONFIGURATION** en haut du fichier `organize_notes.py` pour cibler vos dossiers de recherche personnels.

### Utilisation

Le script est idéal pour un lancement hebdomadaire automatique :

```bash
# Lancement normal
python organize_notes.py
```

---

### Credits / Crédits

The Markdown conversion logic is based on Antigravity's work, and the Skim notes extraction relies on utilities by Christiaan Hofman.

La logique de conversion Markdown s'appuie sur les travaux d'Antigravity, et la conversion des notes Skim sur les utilitaires de Christiaan Hofman.
