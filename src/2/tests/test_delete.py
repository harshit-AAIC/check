import os
import boto3
from mock import patch
from moto import mock_dynamodb2

from create_table import create_table


@mock_dynamodb2
@patch.dict(os.environ, {"DYNAMODB_TABLE": "2-table"})
def test_delete_ok():
    from delete import delete
    create_table()

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    table.put_item(Item={'s': '123'})

    delete_event = {'httpMethod': 'DELETE', 'pathParameters': {'s': '123'}}
    result = delete(delete_event, None)

    assert result['statusCode'] == 200
