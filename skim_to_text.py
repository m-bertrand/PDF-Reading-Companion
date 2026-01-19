#!/usr/bin/env python3
import sys
from biplist import readPlist

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
        'é': r'\u233?',
        'è': r'\u232?',
        'ê': r'\u234?',
        'à': r'\u224?',
        'â': r'\u226?',
        'ô': r'\u244?',
        'û': r'\u251?',
        'ù': r'\u249?',
        'ç': r'\u231?',
        'î': r'\u238?',
        'ï': r'\u239?',
        'ë': r'\u235?',
        'ü': r'\u252?',
        
        # Allemand
        'ä': r'\u228?',
        'ö': r'\u246?',
        'ß': r'\u223?',
        
        # Symboles
        '«': r'\u171?',
        '»': r'\u187?',
        '—': r'\u8212?',
        '–': r'\u8211?',
        
        # Guillemets
        '"': r'\u8220?',
        '"': r'\u8221?',
        ''': r'\u8216?',
        ''': r'\u8217?'
    }
    
    # Fonction pour convertir un caractère en code RTF
    def convert_char(c):
        if c in char_map:
            return char_map[c]
        elif ord(c) < 128:
            return c
        else:
            # Pour les caractères non listés, utiliser leur valeur Unicode
            return f'\\u{ord(c)}?'
    
    # Conversion du texte caractère par caractère
    result = ''
    for char in text:
        result += convert_char(char)
    
    return result

def extract_and_sort_skim_annotations(file_path, output_text_path):
    try:
        print(f"Lecture du fichier : {file_path}")
        plist_data = readPlist(file_path)
        
        annotations = []
        
        if isinstance(plist_data, list):
            for item in plist_data:
                page = item.get("pageIndex")
                contents = item.get("contents", "").strip()
                
                if page is not None and contents:
                    print(f"Extrait - Page {page + 1}: {contents[:50]}...")
                    annotations.append((int(page), contents))
        
        if not annotations:
            print("Aucune annotation trouvée")
            return

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

        print(f"Fichier RTF généré : {output_text_path}")
        
    except Exception as e:
        print(f"Erreur : {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilisation : skim_to_text <chemin_du_fichier.skim>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace(".skim", "_annotations.rtf")
    extract_and_sort_skim_annotations(input_file, output_file)


