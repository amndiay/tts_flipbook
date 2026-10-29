import json
import boto3
import random
import string
import datetime

s3_client = boto3.client("s3")

def generate_journal_id(publication):
    """Génère un journal_id basé sur les 3 premières lettres de la publication et 8 chiffres aléatoires."""
    prefix = publication[:3].upper()  # Extrait les 3 premiers caractères en majuscules
    number = ''.join(random.choices(string.digits, k=8))  # Génère 8 chiffres aléatoires
    return f"{prefix}{number}"

def journal_exists(bucket_name, publication, journal_id):
    """ Vérifie si un journal avec cet ID existe déjà dans S3 """
    prefix = f"featured/{publication}{journal_id}/"  # Chemin de l'objet dans le bucket

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    # Si la liste des objets contient des éléments, c'est que l'ID existe déjà
    return "Contents" in response

def get_publication_metadata(bucket_name, publication):
    """Retourne les métadonnées de l'ensemble des publications."""
    # Récupération du fichier JSON depuis S3
    response = s3_client.get_object(Bucket=bucket_name, Key='metadata/liste.json')
    file_content = response['Body'].read().decode('utf-8')
    
    # Conversion du contenu json en objet Python
    metadata = json.loads(file_content)
    if publication.lower() not in metadata:
        raise ValueError(f"Publication non reconnue : {publication}")
    
    return metadata[publication.lower()]


def create_journal_structure(bucket_name, publication, urlJournal):
    """Crée la structure du journal dans S3."""
    # Obtenir les métadonnées spécifiques à la publication
    pub_metadata = get_publication_metadata(bucket_name, publication)
    # Génération de l'ID et vérification s'il existe dans S3
    while True:
        journal_id = generate_journal_id(publication)
        if not journal_exists(bucket_name, publication, journal_id):  # Si l'ID n'existe pas, on le garde
            break
    publication_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')  # Génère la date du jour en UTC
    base_path = f"featured/{publication}/{journal_id}/"
    
    # Liste des dossiers à créer (sans le dossier audio)
    directories = [
        f"{base_path}images/",
        f"{base_path}pdf/",
        f"{base_path}articles/",
        f"{base_path}audios/"
    ]
    
    # Création des dossiers en ajoutant un fichier vide ".keep"
    for directory in directories:
        s3_client.put_object(Bucket=bucket_name, Key=f"{directory}.keep", Body="")
    
    # Ajout des fichiers par défaut
    default_files = {
        f"{base_path}meta_{journal_id}.json": json.dumps({
            "journal_id": journal_id,
            "description": pub_metadata["description"],
            "publication": publication,
            "publicationDate": publication_date,
            "urlJournal": urlJournal,
            "urlAudio": f"https://{bucket_name}.s3.us-east-1.amazonaws.com/featured/{publication}/{journal_id}/audios/final/",
            "status": "published",
            "featured": "true",
            "category": pub_metadata["category"],
            "tags": pub_metadata["tags"],
            "mainImage": f"{journal_id}.jpg",
            "attachments": [f"pdf_{journal_id}.pdf"],
        }, indent=4)
    }
    
    # Création des fichiers
    for file_path, content in default_files.items():
        s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=content)

    return journal_id  # Retourne l'ID généré pour le journal

def lambda_handler(event, context):
    bucket_name = "myseneditions"  # Remplacez par votre bucket réel
    publication = event.get("publication")
    urlJournal = event.get("urlJournal")
    # Vérification si publication est None
    if not publication:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "La clé 'publication' est requise."})
        }
    journal_id = create_journal_structure(bucket_name, publication, urlJournal)
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"Arborescence creee pour {journal_id} dans {publication}",
            "journal_id": journal_id
        })
    }
