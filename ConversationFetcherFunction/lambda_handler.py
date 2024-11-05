import json
import boto3
import requests
import os
from datetime import datetime

class SentimentAnalyzer:
    def __init__(self, s3_client=None, bucket_name=None):
        self.s3_client = s3_client or boto3.client('s3')
        self.bucket_name = bucket_name or 'workplace-sentiment-analysis'

    def fetch_messages(self, api_url):
        response = requests.get(api_url)
        response.raise_for_status()  
        return response.json()  

    def save_to_s3(self, messages):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        s3_key = f"conversations/{timestamp}_messages.json"  
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=json.dumps(messages)
        )
        return s3_key

def lambda_handler(event, context, sentiment_analyzer=None):
    api_url = "https://15p1n6bcq2.execute-api.us-east-1.amazonaws.com/default/SlackAPIStubFunction"
    
    sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()

    try:
        messages = sentiment_analyzer.fetch_messages(api_url)
        s3_key = sentiment_analyzer.save_to_s3(messages)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Messages saved successfully', 's3_key': s3_key})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

if __name__ == "__main__":
    test_event = {}
    test_context = {}
    print(lambda_handler(test_event, test_context))
