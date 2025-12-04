import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("inventory")

# Optional: encoder in case you want to return deleted item later
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    # 1. Get item_id from path parameters
    path_params = event.get("pathParameters") or {}
    item_id = path_params.get("id")

    if not item_id:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing 'id' path parameter")
        }

    try:
        # 2. Find the item by item_id (we need the sort key too)
        query_resp = table.query(
            KeyConditionExpression=Key("item_id").eq(item_id)
        )
        items = query_resp.get("Items", [])

        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps("Item not found")
            }

        item = items[0]  # assume one item per item_id

        # 3. Delete using full key (PK + SK)
        table.delete_item(
            Key={
                "item_id": item["item_id"],
                "item_location_id": item["item_location_id"]
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": f"Item with ID {item_id} deleted successfully."},
                cls=DecimalEncoder
            )
        }

    except Exception as e:
        print("Error deleting item:", e)
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error deleting item: {str(e)}")
        }