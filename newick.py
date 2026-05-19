import cv2
import pytesseract
from pytesseract import Output
from PIL import Image
import re

# Ustawienie scieski do Tesseract OCR (dostosuj do swojej instalacji)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    """Ekstrakcja tekstu z obrazu za pomocs OCR."""
    # Wczytanie obrazu
    image = cv2.imread(image_path)

    # Konwersja na skals szarosci
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Usycie Tesseract OCR
    text_data = pytesseract.image_to_data(gray, output_type=Output.DICT)
    return text_data

def parse_tree_structure(text_data):
    """
    Budowanie struktury drzewa na podstawie tekstu z OCR.
    Zaksadamy, se tekst jest odczytywany w kolejnosci hierarchicznej.
    """
    tree_dict = {}
    hierarchy = []

    for i, text in enumerate(text_data['text']):
        if text.strip():
            level = text_data['level'][i]
            clean_text = text.strip()
            if level > len(hierarchy):
                hierarchy.append(clean_text)
            elif level == len(hierarchy):
                hierarchy[-1] = clean_text
            else:
                hierarchy = hierarchy[:level-1] + [clean_text]

            # Dodajemy do struktury drzewa
            current_node = tree_dict
            for h in hierarchy[:-1]:
                if h not in current_node:
                    current_node[h] = {}
                current_node = current_node[h]
            current_node[hierarchy[-1]] = {}

    return tree_dict

def convert_to_newick(tree, parent=None):
    """Rekurencyjne przeksztascenie drzewa w format Newick."""
    if isinstance(tree, dict):
        children = [convert_to_newick(v, k) for k, v in tree.items()]
        if parent is None:
            return f"({','.join(children)});"
        return f"({','.join(children)}){parent}"
    else:
        return parent

def save_newick(tree_dict, output_file):
    """Zapis struktury drzewa do pliku w formacie .nwk"""
    newick_str = convert_to_newick(tree_dict)
    with open(output_file, 'w') as f:
        f.write(newick_str)
    print(f"Drzewo zapisano w pliku: {output_file}")

# scieska do obrazu drzewa
image_path = 'Drzewo_NJ_sekwencje_sinice_bootstrap.png'

# 1. Ekstrakcja tekstu z obrazu
text_data = extract_text_from_image(image_path)

# 2. Parsowanie struktury drzewa
tree_dict = parse_tree_structure(text_data)

# 3. Konwersja na format Newick i zapis
output_file = 'drzewo.nwk'
save_newick(tree_dict, output_file)
