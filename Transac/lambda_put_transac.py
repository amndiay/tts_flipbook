import boto3
import json
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Transaction')

def lambda_handler(event, context):
    # Récupérer les données de l'achat depuis l'événement (API Gateway)
    body = json.loads(event['body'])
    transaction_id = str(uuid.uuid4())
    code = str(uuid.uuid4())[:6]  # Génération d'un code d'accès à 6 caractères

    # Ajouter une entrée dans DynamoDB
    table.put_item(
        Item={
            'transaction_id': transaction_id,
            'pub': body['pub'],
            'user_phone': body['user_phone'],
            'item_id': body['item_id'],
            'item_name': body['item_name'],
            'amount': body['amount'],
            'code': code,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

    # Retourner une réponse
    return {
        'statusCode': 201,
        'headers': {
        'Access-Control-Allow-Origin': 'https://dev.d1rwip5pvrnb4u.amplifyapp.com',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({'transaction_id': transaction_id, 'code': code})
    }
