import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key


# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('inventory')

# Encoder to handle Decimal values in JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    # Get item_id from path parameters
    path_params = event.get('pathParameters') or {}
    item_id = path_params.get('id')

    if not item_id:
        return {
            'statusCode': 400,
            'body': json.dumps("Missing 'id' path parameter")
        }

    try:
        # Query DynamoDB for this item_id
        response = table.query(
            KeyConditionExpression=Key('item_id').eq(item_id)
        )

        items = response.get('Items', [])
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found')
            }

        item = items[0]

        return {
            'statusCode': 200,
            'body': json.dumps(item, cls=DecimalEncoder)
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }