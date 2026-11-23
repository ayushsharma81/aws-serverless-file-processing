
import json
import boto3
import os
from urllib.parse import unquote_plus

s3 = boto3.client('s3')

OUTPUT_BUCKET = 'ayush-file-processing-metadata-2026'

ALLOWED_EXTENSIONS = ['.pdf', '.txt', '.csv', '.jpg', '.png']


def lambda_handler(event, context):

    for record in event['Records']:

        input_bucket = record['s3']['bucket']['name']
        file_key = unquote_plus(record['s3']['object']['key'])

        try:
            # Retrieve uploaded file information
            response = s3.head_object(
                Bucket=input_bucket,
                Key=file_key
            )

            file_size = response['ContentLength']
            file_type = os.path.splitext(file_key)[1].lower()

            # Validate file extension
            if file_type not in ALLOWED_EXTENSIONS:
                status = 'Invalid File Type'
            else:
                status = 'Processed'

            # Generate metadata
            metadata = {
                'file_name': os.path.basename(file_key),
                'file_size': file_size,
                'file_type': file_type,
                'status': status
            }

            # Generate JSON output
            output_key = os.path.basename(file_key) + '.json'

            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=json.dumps(metadata, indent=4),
                ContentType='application/json'
            )

            print('File processed:', metadata)

        except Exception as error:
            print('Processing failed:', str(error))
            raise

    return {
        'statusCode': 200,
        'body': json.dumps('File processing completed')
    }
