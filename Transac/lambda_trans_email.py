import json
import urllib.request
import os
import logging

# Configuration du logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Récupérer le token d'accès depuis les variables d'environnement
    whatsapp_access_token = os.getenv('WHATSAPP_TOKEN')
    phone_number_id = os.getenv('PHONE_NUMBER_ID')  # Ajoutez PHONE_NUMBER_ID en variable d'environnement
    # Configurer les détails du message
    to_number = "whatsapp:+221777421973"  # Numéro du destinataire (format international)
    journal_name = "L'observateur'"           # Nom du journal
    access_code = "256sc"                # Code d'accès
    
    url = f"https://graph.facebook.com/v12.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {whatsapp_access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": "transaction",  # Remplacez par le nom exact de votre modèle approuvé
            "language": {"code": "fr"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": access_code},  # Paramètre 1 : Code d'accès
                        {"type": "text", "text": journal_name}    # Paramètre 2 : Nom du journal
                    ]
                }
            ]
        }
    }
    
    # Envoyer le message via l'API WhatsApp
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            logger.info(f"Réponse de l'API WhatsApp (Status: {response.status}): {response_body}")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Message WhatsApp envoyé avec succès!',
                    'response': json.loads(response_body),
                    'timestamp': context.aws_request_id
                })
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error(f"Erreur HTTP lors de l'appel à l'API WhatsApp (Code: {e.code}): {error_body}")
        return {
            'statusCode': e.code,
            'body': f"Erreur HTTP: {error_body}"
        }
    except urllib.error.URLError as e:
        logger.error(f"Erreur réseau lors de l'appel à l'API WhatsApp : {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Erreur réseau: {str(e)}"
        }
