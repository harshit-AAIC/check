import os

import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def delete(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # delete the item from the database
    table.delete_item(
        Key={
            's': event['pathParameters']['s']
        }
    )

    # create a response
    response = {
        "statusCode": 200
    }

    return response