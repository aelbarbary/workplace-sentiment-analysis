import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
BUCKET_NAME = 'workplace-sentiment-analysis'
RESULTS_FOLDER = 'sentiment-analysis-results/'

def fetch_results_from_s3(s3_client, bucket_name, results_folder):
    results = []

    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name, Prefix=results_folder):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if not key.endswith('/'):
                print(f"Processing file: {key}")

                # Fetch the object from S3
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                data = json.loads(response['Body'].read())

                # Extract and parse the timestamp from the file name
                timestamp_str = key.split('/')[-1].replace('analysis_result_', '').replace('.json', '')
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

                # Append both the timestamp and the result data
                results.append({
                    'timestamp': timestamp.isoformat(),  # Convert to ISO format for better readability
                    'result': data
                })

    return results

def lambda_handler(event, context):
    results = fetch_results_from_s3(s3, BUCKET_NAME, RESULTS_FOLDER)

    # Sort results by timestamp
    results.sort(key=lambda x: x['timestamp'])  # Sort by the timestamp key

    return {
        'statusCode': 200,
        'body': json.dumps(results)  # Return the results with timestamps
    }

if __name__ == '__main__':
    # Simulating the event and context for local testing
    test_event = {}  # You can fill this with test data if needed
    test_context = {}  # You can create a mock context if necessary
    response = lambda_handler(test_event, test_context)
    print(response)
