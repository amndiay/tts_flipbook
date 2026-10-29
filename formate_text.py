import re
import os

def process_article(article_text, article_number):
    # Trouver toutes les balises et leur contenu
    balises = re.findall(r'<(\w+)>(.*?)</\1>', article_text, re.DOTALL)
    
    # Traiter chaque balise
    for i, (balise, contenu) in enumerate(balises, start=1):
        # Déterminer le type de fichier (remi ou lea)
        file_type = 'lea' if balise == 's' else 'remi'
        
        # Créer le nom du fichier
        filename = f"article{article_number}-{i}{file_type}.txt"
        
        # Ajouter les balises speak et prosody pour les balises 's'
        if balise == 's':
            contenu = f"<speak>\n  <prosody rate=\"110%\">\n{contenu}\n</prosody>\n</speak>"
        
        filepath = os.path.join(output_dir, filename)
        # Écrire le contenu dans le fichier
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(contenu.strip())

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # Trouver tous les articles
    articles = re.findall(r'\[article\](.*?)\[/article\]', file_content, re.DOTALL)
    
    # Traiter chaque article
    for i, article in enumerate(articles, start=1):
        process_article(article, i)

# Nom du fichier d'entrée
input_filename = "global2.txt"

# Chemin du dossier de sortie
output_dir = "articles"
os.makedirs(output_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas

# Traitement du fichier
process_file(input_filename)
