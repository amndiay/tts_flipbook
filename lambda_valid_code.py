import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Transaction')

def lambda_handler(event, context):
    body = json.loads(event['body'])
    print("Contenu de body:", body)
    pub = body['pub']
    input_code = body['accessCode']
    article_id = body['article_id']

    # Rechercher la transaction dans DynamoDB
    response = table.get_item(Key={'pub': pub, 'code':input_code})

    if 'Item' in response:
        item_id = response['Item']['item_id']
        if article_id == item_id:
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': 'https://dev.d1rwip5pvrnb4u.amplifyapp.com',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'isValid': True})
            }
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': 'https://dev.d1rwip5pvrnb4u.amplifyapp.com',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'isValid': False, 'message': 'Code non valide.'})
            }
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': 'https://dev.d1rwip5pvrnb4u.amplifyapp.com',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'isValid': False, 'message': 'Article inexistant.'})
        }
