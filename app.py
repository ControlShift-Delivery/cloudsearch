from flask import Flask, request, render_template, jsonify
import os
import boto3
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# AWS Credentials from Environment Variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Boto3 Client
client = boto3.client(
    'cloudtrail',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_logs():
    try:
        # Get search parameters from the form
        event_id = request.form.get('eventID')
        user_id = request.form.get('userID')
        start_time = request.form.get('startTime')
        end_time = request.form.get('endTime')
        account_id = request.form.get('accountID')
        region = request.form.get('region')

        # Construct filters
        lookup_attributes = []
        if event_id:
            lookup_attributes.append({"AttributeKey": "EventId", "AttributeValue": event_id})
        if user_id:
            lookup_attributes.append({"AttributeKey": "Username", "AttributeValue": user_id})
        if account_id:
            lookup_attributes.append({"AttributeKey": "AccountId", "AttributeValue": account_id})
        if region:
            lookup_attributes.append({"AttributeKey": "EventSource", "AttributeValue": region})

        # Format datetime
        start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S") if start_time else datetime.utcnow() - timedelta(days=7)
        end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S") if end_time else datetime.utcnow()

        # Fetch logs from CloudTrail
        response = client.lookup_events(
            LookupAttributes=lookup_attributes,
            StartTime=start_time,
            EndTime=end_time,
        )

        events = response.get('Events', [])
        parsed_events = [json.loads(json.dumps(event)) for event in events]  # Parse JSON for readability
        return jsonify(parsed_events)

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
