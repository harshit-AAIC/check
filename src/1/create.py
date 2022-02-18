import json
import logging
import os
import uuid
from datetime import datetime

import boto3

from common.error_responses import NOT_IMPLEMENTED_ERROR_RESPONSE

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def create(event, context):
    data = json.loads(event['body'])
    if not data:
        logging.error("Validation Failed")
        return NOT_IMPLEMENTED_ERROR_RESPONSE

    timestamp = str(datetime.utcnow().timestamp())

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        's': str(uuid.uuid1()),
        
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # write the item to the database
    table.put_item(Item=item)

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(item)
    }

    return response