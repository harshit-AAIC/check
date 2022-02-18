import os
import boto3
from mock import patch
from moto import mock_dynamodb2

from create_table import create_table


@mock_dynamodb2
@patch.dict(os.environ, {"DYNAMODB_TABLE": "22-table"})
def test_update_ok():
    from update import update
    create_table()

    update_event = {'body': 
                    'pathParameters': {'s': '123'},
                    'httpMethod': 'PUT'}
    result = update(update_event, None)

    assert result['statusCode'] == 200

@mock_dynamodb2
@patch.dict(os.environ, {"DYNAMODB_TABLE": "22-table"})
def test_update_error():
    from update import update
    create_table()

    update_event = {'httpMethod': 'PUT', 'pathParameters': {
        's': '123'}, 'body': '{}'}
    result = update(update_event, None)

    assert result['statusCode'] == 501