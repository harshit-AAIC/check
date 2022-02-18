import json
import logging
import os
from datetime import datetime

import boto3

from common.decimalencoder import DecimalEncoder
from error_responses import NOT_IMPLEMENTED_ERROR_RESPONSE

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def update(event, context):
    data = json.loads(event['body'])
    if not data:
        logging.error("Validation Failed")
        return NOT_IMPLEMENTED_ERROR_RESPONSE

    timestamp = str(datetime.utcnow().timestamp())

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    result = table.update_item(
        Key={
            's': event['pathParameters']['s']
        },
        ExpressionAttributeValues={
            ':update_value': next(iter(data.values())),
            ':updatedAt': timestamp,
        },
        UpdateExpression='SET {} = :update_value, updatedAt = :updatedAt'.format(
            next(iter(data.keys()))),
        ReturnValues='ALL_NEW',
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(result['Attributes'],
                           cls=DecimalEncoder)
    }

    return response