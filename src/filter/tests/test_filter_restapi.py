import json
import os
import boto3
import unittest
import pytest

from moto import mock_dynamodb2
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from aws_lambda_powertools import Logger

logger = Logger(service="docuphase-ig-filter")

@mock_dynamodb2
class FilterRestApiTest(unittest.TestCase):

    def setUp(self):
      """
      Create database resource and mock table
      """
      os.environ['AWS_REGION'] = "us-east-1"
      os.environ['FILTER_TABLE'] = "filter-table"  
      os.environ['DISABLE_CORS'] = "True"
      self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
      self.table = self.dynamodb.create_table(
          TableName=os.environ['FILTER_TABLE'],
          KeySchema=[
              {
                  'AttributeName': 'id',
                  'KeyType': 'HASH'
              }
          ],
          AttributeDefinitions=[
              {
                  'AttributeName': 'id',
                  'AttributeType': 'S'
              }
          ],
          ProvisionedThroughput={
              'ReadCapacityUnits': 1,
              'WriteCapacityUnits': 1
          }
      )

    def tearDown(self):
      """
      Delete database resource and mock table
      """
      self.table.delete()
      self.dynamodb=None

    def test_create_ok(self):
        from filter.filter_restapi import create
        create_event = {'body': '{"name": "Name 1", "status": "created", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
        'httpMethod': 'POST'}

        result = create(create_event, LambdaContext)

        assert result['statusCode'] == 201

    def test_create_id_should_not_have_value(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import create
            create_event = {'body' :'{"id": "17hus-78uht-89jfc", "name": "name 1", "status": "Created", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)

    def test_create_filter_criteria_validation(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import create
            create_event = {'body': '{"name": "name 1", "status": "Created"}', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)

    def test_create_name_validation(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import create
            create_event = {'body': '{"status": "Created", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)


    def test_create_status_validation(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import create
            create_event = {"body": '{"name": "name 1", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)


    # Get

    def test_get_ok(self):
        from filter.filter_restapi import get

        get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "name 1",
            "status": "Created",
            "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]
        }

        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['FILTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': '17hus-78uht-89jfc'}}
        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 201

    def test_get_not_found(self):
        from filter.filter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': '17hus-78uht-89jfc'}}

        result = get(get_event, context=LambdaContext)

        assert result['statusCode'] == 404


    def test_get_pathparameter_is_none(self):
        from filter.filter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': None}}

        result = get(get_event, context=LambdaContext)
        assert result['statusCode'] == 404

    def test_get_pathparameter_is_empty(self):

        from filter.filter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': ''}}

        result = get(get_event, context=LambdaContext)
        assert result['statusCode'] == 404

    def test_get_pathparameter_is_missing(self):
        from filter.filter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {}}
        with pytest.raises(KeyError):
            get(get_event, context=LambdaContext)


    # Update

    def test_update_ok(self):
        from filter.filter_restapi import update

        update_event = {'body': '{"id": "17hus-78uht-89jfc", "name": "updated Name", "status": "True", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
        'httpMethod': 'PUT','pathParameters': {'id': '123'}}
        result = update(update_event, context=LambdaContext)

        assert result['statusCode'] == 201

    def test_update_error_with_id_is_missing(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import update
            update_event = {'body': '{"name": "updated Name", "status": "True", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'PUT'}

            result = update(update_event, context=LambdaContext)
    #not done
    def test_update_error_with_id_is_none(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import update
            update_event = {'body': '{"id": null, "name": "updated Name", "status": "True", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'PUT'}

            result = update(update_event, context=LambdaContext)

    def test_update_error_with_id_is_empty(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import update
            update_event = {'body': '{"id": "", "name": "updated Name", "status": "True", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'PUT'}

            result = update(update_event, context=LambdaContext)

    def test_update_error_with_name_missing(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import update
            update_event = {'body': '{"id": "17hus-78uht-89jfc", "status": "True", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'PUT'}

            result = update(update_event, context=LambdaContext)


    def test_update_error_with_status_missing(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import update
            update_event = {'body': '{"id": "17hus-78uht-89jfc", "name": "updated Name", "filter_criteria": [{"key" : "key1", "value": "value1", "condition": "condition1", "operator": "op1"}]}', 
            'httpMethod': 'PUT'}

            result = update(update_event, context=LambdaContext)

    def test_update_error_with_filter_criteria_missing(self):
        with pytest.raises(KeyError):
            from filter.filter_restapi import update
            update_event = {'body': '{"id": "17hus-78uht-89jfc", "name": "updated Name", "status": "True"}', 
            'httpMethod': 'PUT'}

            result = update(update_event, context=LambdaContext)

