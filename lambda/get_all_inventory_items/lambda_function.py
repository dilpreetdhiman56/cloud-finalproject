import boto3
import json
from decimal import Decimal

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("inventory") 

# Encoder so Decimal values can be returned as JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    try:
        # Scan the whole table
        response = table.scan()
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "body": json.dumps({"items": items}, cls=DecimalEncoder)
        }

    except Exception as e:
        print("Error scanning table:", e)
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }