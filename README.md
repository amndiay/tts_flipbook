# TTS Flipbook

A Python-based project for transforming digital flipbook articles into audio content and managing access validation for paid publication access.

This repository contains AWS Lambda functions and supporting scripts that work together to:

- format article text for audio generation,
- create S3 publication structures for featured journals,
- generate speech audio with Amazon Polly,
- store transaction/access-code records in DynamoDB,
- validate purchase codes for article access,
- send WhatsApp notifications for access credentials.

## Project overview

The workflow is designed for a publication platform where users can access digital journal articles in audio format. The platform automatically prepares article text, converts it to MP3 with Polly, and connects purchase validation with a transaction system.

## Features

- Text formatting for articles and sub-articles
- S3-based publication and media organization
- Audio generation from text using Amazon Polly
- DynamoDB transaction storage and code validation
- WhatsApp notification support for delivering access codes
- Lambda-based serverless backend components

## Repository structure

```text
.
├── Audios/
│   ├── ConcaAudio.py
│   └── lambda_text_to_speech.py
├── Transac/
│   ├── lambda_put_transac.py
│   ├── lambda_trans_email.py
│   └── lambda_trans_wh.py
├── formate_text.py
├── lambda_FeaturedPutS3Files.py
├── lambda_FeaturedToArchive.py
├── lambda_valid_code.py
├── .gitattributes
├── .DS_Store
└── README.md
```

## Main components

### 1) Text formatting

`formate_text.py`

This script parses an input text file containing sections wrapped in article tags and creates output text files for each article block. It also detects `s` tags and wraps them with SSML so they can be processed by Polly with voice styling.

Example pattern used:

```text
[article]
<text>...</text>
[/article]
```

### 2) S3 publication setup

`lambda_FeaturedPutS3Files.py`

Creates the folder structure for a featured journal in S3, including:

- `images/`
- `pdf/`
- `articles/`
- `audios/`

It also creates a metadata JSON file describing the journal, publication date, URL, tags, and attachments.

### 3) Audio generation

`Audios/lambda_text_to_speech.py`

Lists article text files from S3, splits large text into manageable chunks, and uses Amazon Polly to convert each chunk into an MP3 file. The script chooses different voices depending on article type (for example, `Lea` for SSML segments and `Remi` for standard text segments).

### 4) Transaction creation and validation

`Transac/lambda_put_transac.py`

Stores purchase transactions in DynamoDB. Each item contains:

- `transaction_id`
- `pub`
- `user_phone`
- `item_id`
- `item_name`
- `amount`
- `code`
- `timestamp`

`lambda_valid_code.py`

Checks whether a provided access code matches the transaction record for the given publication and article ID. This is used to validate whether a user is allowed to access a specific item.

### 5) Notification and delivery

`Transac/lambda_trans_email.py`

Sends a WhatsApp message using the Meta Graph API with an access code and journal name. This is designed for delivering access credentials to users after a purchase.

## AWS stack used

- Amazon S3 for article storage and generated audio files
- Amazon DynamoDB for transaction records and access validation
- AWS Lambda for serverless processing
- Amazon Polly for text-to-speech conversion
- WhatsApp Cloud API for customer communication

## Typical workflow

1. A publication or journal is created in S3.
2. Article text files are uploaded under the publication structure.
3. The audio Lambda reads the text files and converts them to MP3 with Polly.
4. Users make a purchase or access request.
5. A transaction is created in DynamoDB with a generated access code.
6. The access code is sent by WhatsApp or another delivery channel.
7. The validation Lambda confirms the code and article match before granting access.

## Environment and configuration

Several scripts assume AWS resources and environment values are configured. Typical requirements include:

- AWS credentials configured for local or Lambda execution
- S3 bucket name such as `myseneditions`
- DynamoDB table named `Transaction`
- Lambda environment variables for WhatsApp integration, such as:
  - `WHATSAPP_TOKEN`
  - `PHONE_NUMBER_ID`

## Example Lambda event payloads

### Transaction creation

```json
{
  "body": "{\"pub\":\"observateur\",\"user_phone\":\"+221777000000\",\"item_id\":\"article-123\",\"item_name\":\"Edition 01\",\"amount\":\"1500\"}"
}
```

### Access validation

```json
{
  "body": "{\"pub\":\"observateur\",\"accessCode\":\"ABC123\",\"article_id\":\"article-123\"}"
}
```

## Dependencies

This project uses the Python standard library and AWS SDK libraries. The main dependencies are:

- `boto3`
- `json`
- `os`
- `uuid`
- `datetime`
- `re`

Install the AWS SDK with:

```bash
pip install boto3
```

## Quick start

1. Clone the repository.
2. Configure AWS credentials.
3. Set the required S3 and DynamoDB resources.
4. Prepare your publication text and article files.
5. Upload article content to the target S3 publication folder.
6. Invoke the Lambda responsible for audio generation.
7. Run transaction creation and validation flows as needed.

## Notes

- Some values in the repository are hardcoded for a specific environment (for example, AWS bucket names, phone numbers, and frontend origins). These should be moved to environment variables or configuration for production use.
- The project uses French labels in some places, which reflects the business logic and publication context.
- The repository currently appears to be in an early prototype or internal deployment stage.

## Future improvements

- Move hardcoded configuration to environment variables and secret management.
- Add automated tests for Lambda handlers.
- Add CI/CD with linting and deployment automation.
- Improve logging and tracing for production monitoring.
- Add a unified configuration layer for bucket names, API endpoints, and publication metadata.

## License

This project does not currently declare an explicit license file. If you plan to share or distribute it publicly, consider adding a license such as MIT or Apache-2.0.

## Summary

`tts_flipbook` is a serverless publication-to-audio system built around AWS Lambda, S3, DynamoDB, Polly, and WhatsApp. It automates the generation of audio content from editorial articles and connects article access validation with transactions and delivery.

If you want, I can also generate a more polished version tailored specifically for GitHub public usage, or a shorter version optimized for a corporate/internal project showcase.
