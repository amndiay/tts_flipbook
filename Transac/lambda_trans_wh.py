import boto3
import json
from botocore.exceptions import ClientError

# Constantes
MAX_EMAILS_PER_EXECUTION = 5
AWS_REGION = "us-east-1"

# Initialisation des clients AWS
dynamodb = boto3.resource('dynamodb')
ses_client = boto3.client('ses', region_name=AWS_REGION)
processed_events_table = dynamodb.Table('ProcessedEvents')

def lambda_handler(event, context):
    email_count = 0
    for record in event['Records']:
        if email_count >= MAX_EMAILS_PER_EXECUTION:
            print(f"Limite de {MAX_EMAILS_PER_EXECUTION} e-mails atteinte. Arrêt du traitement.")
            break
        
        if record['eventName'] == 'INSERT':
            event_id = record['eventID']
            if not is_event_processed(event_id):
                new_image = record['dynamodb']['NewImage']
                code = parse_dynamodb_type(new_image.get('code', {'S': 'N/A'}))
                item_name = parse_dynamodb_type(new_image.get('item_name', {'S': 'N/A'}))
                
                if process_item(code, item_name):
                    mark_event_as_processed(event_id)
                    email_count += 1
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Traitement terminé. {email_count} e-mails envoyés.')
    }

def is_event_processed(event_id):
    try:
        response = processed_events_table.get_item(Key={'EventId': event_id})
        return 'Item' in response
    except ClientError as e:
        print(f"Erreur lors de la vérification de l'événement : {e}")
        return False

def mark_event_as_processed(event_id):
    try:
        processed_events_table.put_item(Item={'EventId': event_id, 'Processed': True})
    except ClientError as e:
        print(f"Erreur lors du marquage de l'événement comme traité : {e}")

def parse_dynamodb_type(dynamodb_value):
    if 'S' in dynamodb_value:
        return dynamodb_value['S']
    elif 'N' in dynamodb_value:
        return str(dynamodb_value['N'])  # Converti en string pour la concaténation
    else:
        return str(dynamodb_value)

def process_item(code, item_name):
    sender = "amath@anitnow.com"
    recipient = "amath@anitnow.com"
    subject = f"Code d'accès pour {item_name}"
    body_text = f"Votre code d'accès pour le journal {item_name} est: {code}"
    
    try:
        response = ses_client.send_email(
            Destination={'ToAddresses': [recipient]},
            Message={
                'Body': {'Text': {'Charset': 'UTF-8', 'Data': body_text}},
                'Subject': {'Charset': 'UTF-8', 'Data': subject},
            },
            Source=sender,
        )
        print(f"Email envoyé! ID du message : {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e.response['Error']['Message']}")
        return False

