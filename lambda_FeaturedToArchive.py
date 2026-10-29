import boto3
import json

s3_client = boto3.client("s3")

BUCKET_NAME = "myseneditions"  # Remplace par le nom de ton bucket
SOURCE_PREFIX = "featured/"
DESTINATION_PREFIX = "archived/"

def move_featured_to_archived():
    """ Déplace tous les myseneditions de 'featured/' vers 'archived/' """
    
    # Liste tous les objets dans le dossier 'featured/'
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=SOURCE_PREFIX)
    
    if "Contents" not in response:
        return {"message": "Aucun journal à archiver."}
    
    objects = response["Contents"]
    
    for obj in objects:
        source_key = obj["Key"]
        
        # Construire la nouvelle clé dans archived/ en remplaçant 'featured/' par 'archived/'
        destination_key = source_key.replace(SOURCE_PREFIX, DESTINATION_PREFIX, 1)
        
        # Copier l'objet vers 'archived/'
        s3_client.copy_object(
            Bucket=BUCKET_NAME,
            CopySource={"Bucket": BUCKET_NAME, "Key": source_key},
            Key=destination_key
        )

    return {"message": "myseneditions archivés avec succès."}

def lambda_handler(event, context):
    """ Handler principal pour exécuter la fonction de déplacement """
    result = move_featured_to_archived()
    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }
