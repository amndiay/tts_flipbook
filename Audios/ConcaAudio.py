import boto3
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    path_pub = event.get("path_pub") 
    source_bucket = 'myseneditions'
    source_prefix = f'featured/{path_pub}/audios/'
    destination_bucket = 'myseneditions'
    destination_prefix = f'featured/{path_pub}/audios/final/'

    try:
        folders = list_folders(source_bucket, source_prefix)
        for folder in folders:
            mp3_files = list_mp3_files(source_bucket, folder)
            if mp3_files:
                output_key = f"{destination_prefix}{folder.split('/')[-2]}_concat.mp3"
                concatenate_and_upload(source_bucket, mp3_files, destination_bucket, output_key)
        
        return {'statusCode': 200, 'body': 'Concaténation terminée avec succès'}
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return {'statusCode': 500, 'body': 'Erreur lors de la concaténation'}

def list_folders(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter='/')
    return [p['Prefix'] for p in response.get('CommonPrefixes', [])]

def list_mp3_files(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.mp3')]

def concatenate_and_upload(source_bucket, mp3_files, dest_bucket, output_key):
    concatenated_data = io.BytesIO()

    for file in mp3_files:
        response = s3.get_object(Bucket=source_bucket, Key=file)
        concatenated_data.write(response['Body'].read())
    
    concatenated_data.seek(0)
    s3.put_object(Bucket=dest_bucket, Key=output_key, Body=concatenated_data)
    print(f"Fichier concaténé uploadé: {output_key}")
