import json
import random

employees = ["Alice", "Bob", "Charlie", "David", "Eva"]
messages = [
    "I finished the project ahead of schedule!",
    "Can someone review my code?",
    "What time is the meeting tomorrow?",
    "I'm having trouble with the latest update.",
    "Great job on the presentation, team!",
    "Does anyone have the latest sales figures?",
    "Looking forward to the team lunch!",
    "I think we should consider a different approach."
]

def lambda_handler(event, context):
    # Set the number of messages to return
    num_messages = event.get('num_messages', 5)  
    generated_messages = []

    for _ in range(num_messages):
        employee = random.choice(employees)
        message = random.choice(messages)
        random_message = {
            'employee': employee,
            'message': message,
            'timestamp': context.aws_request_id 
        }
        generated_messages.append(random_message)
    
    return {
        'statusCode': 200,
        'body': json.dumps(generated_messages)
    }