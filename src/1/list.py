import base64
import json
import os

import boto3

from common.decimalencoder import DecimalEncoder
from common.error_responses import INVALID_TOKEN_RESPONSE

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def list(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    if event['queryStringParameters']:
        pagination_token = event['queryStringParameters'].get(
            'pagination_token')
        limit = int(event['queryStringParameters'].get('limit', 20))
    else:
        pagination_token = None
        limit = 20

    if pagination_token:
        try:
            pagination_token_bytes = pagination_token.encode("ascii")
            decoded_binary_secret = base64.b64decode(pagination_token_bytes)
            decoded_token = decoded_binary_secret.decode("ascii")
            exclusive_start_key = {'id': decoded_token}
        except:
            return INVALID_TOKEN_RESPONSE

        result = table.scan(Limit=limit, ExclusiveStartKey=exclusive_start_key)
    else:
        result = table.scan(Limit=limit)

    data = result['Items']

    if 'LastEvaluatedKey' in result:
        lek = result['LastEvaluatedKey']['id']
        lek_bytes = lek.encode("ascii")
        pagination_token_bytes = base64.b64encode(lek_bytes)
        pagination_token = pagination_token_bytes.decode("ascii")
    else:
        pagination_token = ""

    response = {
        "statusCode": 200,
        "headers": {
            "pagination_token": pagination_token
        },
        "body": json.dumps(data, cls=DecimalEncoder)
    }

    return response
