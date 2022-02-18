import json
import os

import boto3

from common.decimalencoder import DecimalEncoder
from common.error_responses import NOT_FOUND_RESPONSE

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def get(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
    result = table.get_item(
        Key={
            's': event['pathParameters']['s']
        }
    )

    if 'Item' in result:
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Item'],
                               cls=DecimalEncoder)
        }

        return response

    return NOT_FOUND_RESPONSE