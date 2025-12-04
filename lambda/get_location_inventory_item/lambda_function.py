import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key


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
    # 1. Get location_id from path parameters
    path_params = event.get("pathParameters") or {}
    location_id = path_params.get("id")

    if location_id is None:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing 'id' path parameter")
        }

    try:
        # Convert to int (DynamoDB attribute is Number)
        location_id_int = int(location_id)
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps("Invalid location id, must be a number")
        }

    try:
        # 2. Query using the GSI: location-index
        response = table.query(
            IndexName="location-index",
            KeyConditionExpression=Key("item_location_id").eq(location_id_int)
        )

        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"location_id": location_id_int, "items": items},
                cls=DecimalEncoder
            )
        }

    except Exception as e:
        print("Error querying by location:", e)
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }