import json
import boto3
from flask import Flask, jsonify
from transformers import pipeline
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

# Initialize the sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis")

# Initialize the S3 client
s3 = boto3.client('s3')
BUCKET_NAME = 'workplace-sentiment-analysis'
CONVERSATIONS_FOLDER = 'conversations/'
ARCHIVE_FOLDER = 'conversation_archive/'
RESULTS_FOLDER = 'sentiment-analysis-results/'

def analyze_sentiment(messages):
    total_score = 0
    positive_count = 0
    negative_count = 0
    message_count = len(messages)

    for message in messages:
        sentiment = sentiment_analyzer(message)[0]
        score = sentiment['score']
        total_score += score

        if sentiment['label'] == 'POSITIVE':
            positive_count += 1
        else:
            negative_count += 1

    avg_sentiment = "POSITIVE" if positive_count >= negative_count else "NEGATIVE"
    avg_score = total_score / message_count if message_count > 0 else 0

    result = {
        'average_sentiment': avg_sentiment,
        'average_score': avg_score,
        'total_messages': message_count,
        'positive_messages': positive_count,
        'negative_messages': negative_count,
    }
    
    return result

def save_result_to_s3(result, timestamp):
    print(f"Saving analysis result to S3")
    result_key = f"{RESULTS_FOLDER}analysis_result_{timestamp}.json"
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=result_key,
        Body=json.dumps(result)
    )
    print(f"Saved analysis result to S3: {result_key}")
    
def merge_all_conversations():
    all_messages = []
    keys_to_archive = []

    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=CONVERSATIONS_FOLDER):
        for obj in page.get('Contents', []):
            key = obj['Key']
            # Ensure the key represents a file, not a folder
            if not key.endswith('/'):
                print(f"Processing file: {key}")
                response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                data = json.loads(response['Body'].read())
                all_messages.extend(entry['message'] for entry in data)
                keys_to_archive.append(key)

    return all_messages, keys_to_archive

def archive_conversations(keys_to_archive):
    for key in keys_to_archive:
        archive_key = key.replace(CONVERSATIONS_FOLDER, ARCHIVE_FOLDER)
        s3.copy_object(Bucket=BUCKET_NAME, CopySource={'Bucket': BUCKET_NAME, 'Key': key}, Key=archive_key)
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)

def process_all_messages():
    print("Processing all conversations...")
    all_messages, keys_to_archive = merge_all_conversations()
    result = None
    if all_messages:
        result = analyze_sentiment(all_messages)
        print("result", result)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(f"Timestamp: {timestamp}")
        save_result_to_s3(result, timestamp)

        archive_conversations(keys_to_archive)
        
    return result

scheduler = BackgroundScheduler()
scheduler.add_job(func=process_all_messages, trigger="interval", minutes=1)
scheduler.start()

@app.route('/')
def index():
    return "Sentiment Analysis Service is running!"

@app.route('/analyze', methods=['GET'])
def aggregate_analysis():
    all_messages, keys_to_archive = merge_all_conversations()
    if all_messages:
        result = analyze_sentiment(all_messages)
        archive_conversations(keys_to_archive)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_result_to_s3(result, timestamp)
        return jsonify(result), 200
    else:
        return jsonify({'error': 'No messages found for analysis'}), 404

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
