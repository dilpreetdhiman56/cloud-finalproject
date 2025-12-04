import json
import boto3
import uuid
from decimal import Decimal


def lambda_handler(event, context):
    # Parse incoming JSON data
    try:
        data = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps("Bad request. Please provide the data.")
        }

    # DynamoDB setup
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Inventory')

    # Generate a unique ID
    unique_id = str(uuid.uuid4())

    try:
        item = {
            "item_id": unique_id,
            "item_name": data["item_name"],
            "item_description": data["item_description"],
            "item_quantity": Decimal(str(data["item_quantity"])),
            "item_price": Decimal(str(data["item_price"])),
            "item_location_id": int(data["item_location_id"])
        }
        return {
            'statusCode': 200,
            'body': json.dumps(f"Item with ID {unique_id} added successfully.")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error adding item: {str(e)}")
        }