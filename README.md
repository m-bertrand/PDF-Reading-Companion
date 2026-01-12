# 📚 SkimKnowledge-Automator

> **"Le présent est gros de l'avenir."** — Transformez vos annotations PDF en une base de connaissances structurée.

Ce script automatise l'extraction, la formalisation et l'indexation des notes prises avec l'application **Skim** (macOS). Il convertit vos annotations binaires en fichiers Markdown enrichis par NLP pour une intégration fluide dans votre second cerveau (**Obsidian**, **Logseq**, etc.).

## ✨ Nouvelles Fonctionnalités
- **Standardisation NLP** : Utilisation de la lemmatisation (Spacy `fr_core_news_sm`) pour des tags cohérents (ex: *concepts* -> *concept*).
- **Mode Dry Run** : Testez le scan et l'analyse sans écrire de fichiers sur le disque.
- **Gestion Robuste des Dépendances** : Utilisation de `sys.executable` pour une portabilité totale.

## 🛠️ Installation

1. **Prérequis** : macOS et [Skim](https://skim-app.sourceforge.io/).
2. **Installation des dépendances** :
   ```bash
   pip install spacy striprtf
   python -m spacy download fr_core_news_sm
