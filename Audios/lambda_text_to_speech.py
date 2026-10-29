import boto3
import os

# Configuration
S3_BUCKET = "myseneditions"
MAX_TEXT_LENGTH = 3000

s3_client = boto3.client("s3")
polly_client = boto3.client("polly")

def list_article_files(publication):
    """
    Liste tous les fichiers texte présents dans les dossiers articles de S3.
    """
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"featured/{publication}")

    article_files = []
    if "Contents" in response:
        for obj in response["Contents"]:
            if "/articles/" in obj["Key"] and obj["Key"].endswith(".txt"):
                article_files.append(obj["Key"])
    
    return article_files

def split_text(text, max_length=MAX_TEXT_LENGTH):
    """
    Découpe le texte en segments tout en évitant de couper les mots.
    """
    parts = []
    while len(text) > max_length:
        split_index = text.rfind(" ", 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(text[:split_index].strip())
        text = text[split_index:].strip()
    if text:
        parts.append(text)
    return parts

def text_to_speech(text, output_path, voice_id, text_type, engine):
    """
    Convertit le texte en audio avec la voix spécifiée de Polly.
    """
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        LanguageCode="fr-FR",
        VoiceId=voice_id,
        TextType=text_type,
        Engine=engine  # Utilisation du moteur generative pour les deux voix
    )
    audio_stream = response["AudioStream"].read()
    with open(output_path, "wb") as file:
        file.write(audio_stream)

def process_article(s3_key):
    """
    Traite un fichier texte depuis S3 et génère des fichiers audio.
    """
    # Extraire les composants du chemin
    path_components = s3_key.split('/')
    journal = path_components[1]  # ex: observateur
    edition = path_components[2]  # ex: OBS21103366
    article_name = os.path.splitext(path_components[-1])[0]  # ex: article1

    # Déterminer la voix à utiliser
    if "lea" in article_name.lower():
        voice_id = "Lea"
        text_type = "ssml"
        engine = "neural"
    else:
        voice_id = "Remi"
        text_type = "text"
        engine = "generative"

    local_text_path = f"/tmp/{article_name}.txt"

    # Télécharger le fichier texte depuis S3
    s3_client.download_file(S3_BUCKET, s3_key, local_text_path)

    # Lire et découper le texte
    with open(local_text_path, "r", encoding="utf-8") as file:
        text_content = file.read()
    text_segments = split_text(text_content)

    # Générer les fichiers audio et les uploader sur S3
    uploaded_files = []
    for idx, segment in enumerate(text_segments):
        local_audio_path = f"/tmp/{article_name}_part{idx+1}.mp3"
        text_to_speech(segment, local_audio_path, voice_id, text_type, engine)
        
        # Définir le chemin S3 pour le fichier audio
        s3_audio_key = f"featured/{journal}/{edition}/audios/{article_name.split('-')[0]}/{article_name}_part{idx+1}.mp3"
        
        # Uploader le fichier audio sur S3
        s3_client.upload_file(local_audio_path, S3_BUCKET, s3_audio_key)
        uploaded_files.append(f"s3://{S3_BUCKET}/{s3_audio_key}")

        # Supprimer le fichier audio local
        os.remove(local_audio_path)

    # Supprimer le fichier texte local
    os.remove(local_text_path)

    return f"Fichiers audio générés et stockés : {', '.join(uploaded_files)}"

def lambda_handler(event, context):
    """
    Fonction Lambda principale qui récupère tous les fichiers articles et les convertit en audio.
    """
    publication = event.get("publication")
    article_files = list_article_files(publication)

    if not article_files:
        return {"statusCode": 404, "message": "Aucun fichier article trouvé."}

    results = []
    for s3_key in article_files:
        try:
            result = process_article(s3_key)
            results.append(result)
        except Exception as e:
            print(f"Erreur lors du traitement de {s3_key}: {e}")

    return {"statusCode": 200, "message": "Traitement terminé", "results": results}
