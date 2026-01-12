import os
import sys
import shutil
import re
from pathlib import Path
import datetime
from collections import Counter
import csv
import spacy
import subprocess
from striprtf.striprtf import rtf_to_text
from biplist import readPlist

# Configuration
# Base directory for downloads (platform independent)
DOWNLOADS_DIR = Path.home() / "Downloads"

# List of folders to watch within the Downloads directory
WATCHED_SUBFOLDERS = [
    "Philosophie",
    "SES",
    "Recherche"
]

# Generate source paths dynamically
SOURCE_DIRS = [DOWNLOADS_DIR / folder for folder in WATCHED_SUBFOLDERS]

# Destination directory for parsed notes
DEST_DIR = DOWNLOADS_DIR / "Notes prises sur PDFs"

# Global NLP model (lazy loaded)
_nlp = None

# --- Internal Skim Conversion Logic (formerly skim_to_text.py) ---

def create_rtf_header():
    """Crée l'en-tête RTF avec support multilingue"""
    return ('{\\rtf1\\ansi\\ansicpg1252\\uc1\n'
            '{\\fonttbl'
            '{\\f0\\froman\\fcharset0\\fprq2 Times New Roman;}'
            '{\\f1\\fnil\\fcharset2\\fprq2 Symbol;}'  # Pour les caractères grecs
            '{\\f2\\fnil\\fcharset0\\fprq2 Arial Unicode MS;}'  # Pour les caractères spéciaux
            '}\n'
            '{\\colortbl;\\red255\\green255\\blue255;}\n'
            '\\f0\\fs28\n'
            '\\margl1440\\margr1440\\paperw11900\\paperh16840\n')

def format_rtf_text(text):
    """Formate le texte pour le RTF avec support multilingue"""
    if text is None:
        return ""
    
    # Dictionnaire des caractères spéciaux
    char_map = {
        # Français
        'é': r'\u233?', 'è': r'\u232?', 'ê': r'\u234?', 'à': r'\u224?',
        'â': r'\u226?', 'ô': r'\u244?', 'û': r'\u251?', 'ù': r'\u249?',
        'ç': r'\u231?', 'î': r'\u238?', 'ï': r'\u239?', 'ë': r'\u235?',
        'ü': r'\u252?',
        # Allemand
        'ä': r'\u228?', 'ö': r'\u246?', 'ß': r'\u223?',
        # Symboles
        '«': r'\u171?', '»': r'\u187?', '—': r'\u8212?', '–': r'\u8211?',
        # Guillemets
        '"': r'\u8220?', '"': r'\u8221?', "'": r'\u8216?', "'": r'\u8217?'
    }
    
    def convert_char(c):
        if c in char_map:
            return char_map[c]
        elif ord(c) < 128:
            return c
        else:
            return f'\\u{ord(c)}?'
    
    result = ''
    for char in text:
        result += convert_char(char)
    return result

def convert_skim_to_rtf(file_path, output_text_path):
    """Extracts annotations from .skim plist and writes to RTF."""
    try:
        # print(f"Lecture du fichier : {file_path}")
        plist_data = readPlist(file_path)
        
        annotations = []
        
        if isinstance(plist_data, list):
            for item in plist_data:
                page = item.get("pageIndex")
                contents = item.get("contents", "").strip()
                
                if page is not None and contents:
                    annotations.append((int(page), contents))
        
        if not annotations:
            # print(f"Aucune annotation trouvée dans {file_path.name}")
            return False

        annotations.sort(key=lambda x: x[0])

        with open(output_text_path, 'w', encoding='utf-8') as f:
            f.write(create_rtf_header())
            
            for page, contents in annotations:
                f.write('\\par\\par\n')
                # Numéro de page en gras
                f.write('{\\b Page ')
                f.write(str(page + 1))
                f.write(':}\\par\n')
                # Contenu avec retrait
                f.write('\\li720 ')
                f.write(format_rtf_text(contents))
                f.write('\\li0\\par\n')
            
            f.write('}')
            
        return True
        
    except Exception as e:
        print(f"Erreur lors de la conversion de {file_path.name} : {str(e)}")
        return False


def find_latest_previous_output_dir(base_dir, current_output_dir_name):
    """Find the most recent previous output directory based on date pattern."""
    candidates = []
    pattern = re.compile(r"Notes en markdown - (\d{4}-\d{2}-\d{2})")
    
    for entry in base_dir.iterdir():
        if entry.is_dir() and entry.name != current_output_dir_name:
            match = pattern.match(entry.name)
            if match:
                date_str = match.group(1)
                candidates.append((date_str, entry))
    
    # Sort by date descending
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    if candidates:
        return candidates[0][1]
    return None

def get_previous_reading_date(md_file_path):
    """Extract 'Dernière lecture' date from an existing markdown file."""
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            # Read first 20 lines (header usually at top)
            for _ in range(20):
                line = f.readline()
                if not line: break
                match = re.search(r'\*\*Dernière lecture\*\*:\s*(\d{4}-\d{2}-\d{2})', line)
                if match:
                    return match.group(1)
    except Exception:
        pass
    return None

def get_nlp():
    global _nlp
    if _nlp is None:
        try:
            print("Loading Spacy model...")
            _nlp = spacy.load("fr_core_news_sm")
        except Exception as e:
            print(f"Failed to load Spacy: {e}")
    return _nlp

def setup_directories():
    """Ensure destination and source directories exist."""
    # Create destination directory
    if not DEST_DIR.exists():
        DEST_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created destination directory: {DEST_DIR}")
        
    # Create source directories if they don't exist
    for source_dir in SOURCE_DIRS:
        if not source_dir.exists():
            source_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created source directory: {source_dir}")

def is_skim_textualized(file_path):
    """
    Check if the file content matches the textualized skim structure.
    Looking for patterns like 'Page X:'
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2048) # Read first 2KB to check potential structure
            if re.search(r'Page\s+\d+:', content, re.IGNORECASE):
                return True
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return False

def has_skim_companion(file_path):
    """Check if there is a corresponding .skim file in the same directory."""
    parent = file_path.parent
    stem = file_path.stem
    
    # Check exact match stem.skim
    if (parent / f"{stem}.skim").exists():
        return True
    
    # Check if removing "_annotations" suffix matches
    if stem.endswith("_annotations"):
        original_stem = stem.replace("_annotations", "")
        if (parent / f"{original_stem}.skim").exists():
            return True
            
    return False

def get_skim_companion_path(file_path):
    """Return the path to the corresponding .skim file if it exists."""
    parent = file_path.parent
    stem = file_path.stem
    
    # Check exact match stem.skim
    p1 = parent / f"{stem}.skim"
    if p1.exists():
        return p1
    
    # Check if removing "_annotations" suffix matches
    if stem.endswith("_annotations"):
        original_stem = stem.replace("_annotations", "")
        p2 = parent / f"{original_stem}.skim"
        if p2.exists():
            return p2
            
    return None

def scan_files():
    """Scan source directories and return list of relevant .rtf files (without moving them)."""
    found_files = []
    
    for source_dir in SOURCE_DIRS:
        if not source_dir.exists():
            print(f"Directory not found, skipping: {source_dir}")
            continue
            
        print(f"Scanning {source_dir}...")
        
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            
            # Skip destination directory if it is inside source (to avoid recursion)
            if DEST_DIR in root_path.parents or root_path == DEST_DIR:
                continue
                
            for file in files:
                if not file.lower().endswith('.rtf'):
                    continue
                    
                file_path = root_path / file
                
                # Filter logic
                if has_skim_companion(file_path) or is_skim_textualized(file_path):
                    found_files.append(file_path)
                        
    return found_files

def extract_content_from_rtf(file_path):
    """Extract relevant text from RTF using striprtf library."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Convert the entire RTF to plain text first
        text = rtf_to_text(content, errors="ignore")
        
        # Now parse the textualized format (Page X: ...)
        matches = []
        # Pattern to find "Page X:" blocks in the plain text
        # This assumes the conversion keeps "Page X:" recognizable
        pattern = re.compile(r'(Page\s+\d+:\s*)([\s\S]*?)(?=(?:Page\s+\d+:)|$)', re.IGNORECASE)
        
        for match in pattern.finditer(text):
            header = match.group(1).strip()
            body = match.group(2).strip()
            
            if body:
                matches.append({"header": header, "text": body})
                
        return matches
        
    except Exception as e:
        print(f"Error extracting content from {file_path}: {e}")
        return []

def analyze_concepts(text_blocks):
    """Analyze text using Spacy with strict cleaning."""
    nlp = get_nlp()
    if not nlp:
        return []
    
    full_text = " ".join([b['text'] for b in text_blocks])
    if len(full_text) > 100000:
        full_text = full_text[:100000]
        
    doc = nlp(full_text)
    
    concepts = []
    custom_stops = {'page', 'note', 'vol', 'chapitre', 'partie', 'chose', 'cas', 'fait', 'fois', 'façon', 'manière'}
    
    def clean_term(text):
        text = text.lower().strip()
        text = re.sub(r'^(le |la |les |l\'|un |une |des |du |de |d\'|ce |cet |cette |ces |son |sa |ses |mon |ma |mes |notre |votre |leur )', '', text)
        return text.strip()

    relevant_labels = ['PER', 'LOC', 'ORG', 'MISC'] 
    for ent in doc.ents:
        if ent.label_ in relevant_labels and len(ent.text) > 2:
            # Use lemma_ to normalize (e.g., avoid plural duplicates)
            term = clean_term(ent.lemma_)
            if term not in nlp.Defaults.stop_words and term not in custom_stops:
                concepts.append(term)
            
    for chunk in doc.noun_chunks:
        if len(chunk.text) > 3:
             # Use lemma_ to normalize
             term = clean_term(chunk.lemma_)
             # Filter out pure digits, single chars, or stop words
             if len(term) < 3: continue
             if term in nlp.Defaults.stop_words: continue
             if term in custom_stops: continue
             if term.isdigit(): continue
             # Filter out "page N"
             if re.search(r'^page\s*\d+$', term): continue
             concepts.append(term)

    counter = Counter(concepts)
    unique_concepts = [c for c, count in counter.most_common(15)]
    return unique_concepts



def generate_individual_notes(file_list, output_dir, previous_output_dir=None):
    """Generate MD files from a list of source files (read-only)."""
    print(f"Generating markdown files in {output_dir}...")
    if previous_output_dir:
        print(f"Comparing against previous generation: {previous_output_dir.name}")
    
    index_links = []
    skipped_count = 0
    
    for file_path in file_list:
        md_filename = f"{file_path.stem}.md"
        md_filename = re.sub(r'[\\/*?:"<>|]', "", md_filename)
        md_file_path = output_dir / md_filename
        
        # --- Incremental Check ---
        # 1. Calculate current reading date
        skim_path = get_skim_companion_path(file_path)
        target_path_for_date = skim_path if skim_path else file_path
        try:
            mtime = target_path_for_date.stat().st_mtime
            current_mod_date = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except:
            current_mod_date = None

        should_process = True
        if previous_output_dir and current_mod_date:
            prev_md_path = previous_output_dir / md_filename
            if prev_md_path.exists():
                prev_date = get_previous_reading_date(prev_md_path)
                if prev_date and current_mod_date <= prev_date:
                    should_process = False
        
        if not should_process:
            skipped_count += 1
            continue
        # -------------------------

        extracted_data = extract_content_from_rtf(file_path)
        
        if not extracted_data:
            continue
            
        content = []
        content.append(f"# {file_path.stem}")
        content.append(f"**Source**: `{file_path.name}`")
        
        if current_mod_date:
            content.append(f"**Dernière lecture**: {current_mod_date}")
        else:
             content.append("**Dernière lecture**: Inconnue")
             
        content.append(f"**Généré le**: {datetime.date.today()}")
        content.append("")
        
        concepts = analyze_concepts(extracted_data)
        if concepts:
            content.append("## 🧠 Concepts clés")
            content.append(", ".join([f"`{c}`" for c in concepts]))
            content.append("")
            # Obsidian tags
            tags = []
            for c in concepts[:5]:
                tag = c.replace(' ', '_').replace("'", "")
                tags.append(f"#{tag}")
            content.append("tags: " + " ".join(tags))
            content.append("")
        
        content.append("## Notes")
        for block in extracted_data:
            content.append(f"### {block['header']}")
            content.append(f"{block['text']}")
            content.append("")
            
        try:
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            print(f"Generated: {md_file_path.name}")
            # Relative link within the Dated Folder context
            index_links.append(f"- [{file_path.stem}]({re.sub(' ', '%20', md_filename)})")
        except Exception as e:
            print(f"Failed to write {md_filename}: {e}")
            
    print(f"Skipped {skipped_count} files (already up to date in previous folder).")
    return index_links

def run_skim_automation():
    """Runs the Skim automation via AppleScript ONLY to save open docs."""
    print("Running Skim automation (Save only)...")
    
    applescript = """
    tell application "System Events"
        set isSkimRunning to (exists (process "Skim"))
    end tell
    
    if isSkimRunning then
        tell application "Skim"
            -- Save all modified docs
            repeat with doc in documents
                if modified of doc then
                    save doc
                end if
            end repeat
        end tell
    end if
    """
    
    try:
        # Run the AppleScript using subprocess
        # using 'osascript -e' requires caution with quoting, so input via stdin is safer for large blocks
        process = subprocess.run(['osascript', '-'], input=applescript, text=True, capture_output=True)
        
        if process.returncode != 0:
            print(f"Skim automation warning (osascript): {process.stderr}")
        else:
            if process.stdout.strip():
                print(f"Skim automation output: {process.stdout}")
                
    except Exception as e:
        print(f"Failed to run Skim automation: {e}")

def batch_convert_skim_files():
    """
    Scans SOURCE_DIRS for .skim files and converts them using internal logic.
    Checks timestamps to avoid redundant processing.
    """
    print("Batch converting .skim files in source directories...")
    
    count = 0 
    for source_dir in SOURCE_DIRS:
        if not source_dir.exists():
            continue
            
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".skim"):
                    skim_path = Path(root) / file
                    target_rtf = skim_path.with_suffix('.rtf')
                    
                    should_run = True
                    if target_rtf.exists():
                        if target_rtf.stat().st_mtime > skim_path.stat().st_mtime:
                            should_run = False
                    
                    if should_run:
                        if convert_skim_to_rtf(skim_path, target_rtf):
                            print(f"Converted: {file}")
                            count += 1
                        else:
                            # It returns False if no annotations or error
                            pass

    if count > 0:
        print(f"Batch conversion finished: {count} files updated.")
    else:
        print("Batch conversion: All files up to date.")

def main():
    print("Starting organization script (Non-destructive)...")
    
    # Run Skim Automation First (for open unsaved docs)
    run_skim_automation()
    
    # Run Batch Conversion (for all files on disk)
    batch_convert_skim_files()
    
    setup_directories()
    
    # 1. Scan for files in source directories (read-only)
    found_files = scan_files()
    if found_files:
        print(f"Found {len(found_files)} files to process.")
    
    # 2. Prepare Output Directory (Dated)
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    output_dir_name = f"Notes en markdown - {today_str}"
    current_output_dir = DEST_DIR / output_dir_name
    
    if not current_output_dir.exists():
        current_output_dir.mkdir(parents=True, exist_ok=True)
        
    # 3. Find Previous Output Directory
    previous_output_dir = find_latest_previous_output_dir(DEST_DIR, output_dir_name)
    
    # 4. Generate Notes
    # We process found_files which are now back in their source locations
    links = generate_individual_notes(found_files, output_dir=current_output_dir, previous_output_dir=previous_output_dir)
    
    # 5. Generate Batch Index
    batch_index_file = current_output_dir / "Index.md"
    content = [f"# Index des Lectures - {today_str}", ""]
    content.append(f"Nombre de documents traités : {len(links)}")
    content.append("")
    content.extend(sorted(links))
    
    try:
        with open(batch_index_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))
        print(f"Index generated at: {batch_index_file}")
    except Exception as e:
        print(f"Failed to write index: {e}")
    
    print("Done.")

if __name__ == "__main__":
    main()
