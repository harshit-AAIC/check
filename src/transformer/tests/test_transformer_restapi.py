import os
import pytest
import unittest
from moto import mock_dynamodb2
import boto3

from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from aws_lambda_powertools import Logger


logger = Logger(service="docuphase-ig-transformer")

@mock_dynamodb2
class TransformerRestApiTest(unittest.TestCase):

    def setUp(self):
      """
      Create database resource and mock table
      """
      os.environ['AWS_REGION'] = "us-east-1"
      os.environ['TRANSFORMER_TABLE'] = "transformer-table"  
      self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
      self.table = self.dynamodb.create_table(
          TableName=os.environ['TRANSFORMER_TABLE'],
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
        from transformer.transformer_restapi import create
        create_event = {'body':'{"name": "Oracle Transformer", "status": "Created", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id" : "1", "name": "tests"} }', 
        'httpMethod': 'POST'}

        result = create(create_event, LambdaContext)

        assert result['statusCode'] == 201

    def test_create_id_should_not_have_value(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import create
            create_event = {'body':'{"id": "91b42ce6-25b6-11ec-9003-1e80801e978", "name": "Oracle Transformer", "status": "Created", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id" : "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)

    def test_create_mapping_validation_exception(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import create
            create_event = {'body': '{"name": "Oracle Transformer", "input_payload": {"S.No" : "1", "first name": "tests"}, "status": "Created"}', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)

    def test_create_name_validation_exception(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import create
            create_event = {'body': '{"status": "Created", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }',
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)

    def test_create_status_validation_exception(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import create
            create_event = {'body': '{"name": "Oracle transformer", "desc": "description", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = create(create_event, LambdaContext)

    def test_get_ok(self):
        from transformer.transformer_restapi import get

        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['TRANSFORMER_TABLE'])
        table.put_item(Item={'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'})

        get_event = {'httpMethod': 'GET',
                    'pathParameters': {'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'}}

        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 201

    def test_get_not_found(self):
        from transformer.transformer_restapi import get

        get_event = {'httpMethod': 'GET',
                    'pathParameters': {'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'}}

        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 404

    def test_get_pathparameter_is_none(self):
        from transformer.transformer_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': None}}

        result = get(get_event, LambdaContext)
        
    def test_get_pathparameter_is_empty(self):
        from transformer.transformer_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': ''}}

        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 404

    def test_get_pathparameter_is_missing(self):
        from transformer.transformer_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {}}

        result = get(get_event, LambdaContext)
        assert result['statusCode'] == 404

    def test_update_ok(self):
        from transformer.transformer_restapi import update

        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['TRANSFORMER_TABLE'])
        # table.put_item(Item={"id": "91b42ce6-25b6-11ec-9003-1e80801e9786"})
        update_event = {'body':'{"id": "91b42ce6-25b6-11ec-9003-1e80801e9786", "name": "Updated Oracle Transformer", "status": "Published", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
                         'pathParameters': {'id': '123'},'httpMethod': 'POST'}

        result = update(update_event, LambdaContext)

        assert result['statusCode'] == 201

    def test_update_error_with_id_is_missing(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import update
            update_event = {'body': '{"name": "Updated Oracle Transformer", "desc": "Updated description", "status": "Published", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = update(update_event, LambdaContext)

    def test_update_error_with_id_is_none(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import update
            update_event = {'body': '{"id": null, "name": "Updated Oracle Transformer", "status": "Published", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = update(update_event, LambdaContext)

    def test_update_error_with_id_is_empty(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import update
            update_event = {'body': '{"id": "", "name": "Updated Oracle Transformer", "status": "Published", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = update(update_event, LambdaContext)

    def test_update_error_with_name_missing(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import update
            update_event = {'body': '{"id": "91b42ce6-25b6-11ec-9003-1e80801e9786", "status": "Published", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = update(update_event, LambdaContext)

    def test_update_error_with_status_missing(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import update
            update_event = {'body': '{"id": "91b42ce6-25b6-11ec-9003-1e80801e9786", "name": "Oracle Transformer", "input_payload": {"S.No" : "1", "first name": "tests"}, "mapping_payload": {"id": "1", "name": "tests"} }', 
            'httpMethod': 'POST'}

            result = update(update_event, LambdaContext)

    def test_update_error_with_mapping_missing(self):
        with pytest.raises(KeyError):
            from transformer.transformer_restapi import update
            update_event = {'body': '{"id": "91b42ce6-25b6-11ec-9003-1e80801e9786", "name": "Oracle Transformer", "desc": "Updated description", "status": "Published", "input_payload": {"S.No" : "1", "first name": "tests"} }', 
            'httpMethod': 'POST'}

            result = update(update_event, LambdaContext)

    def test_transform_ok(self):
        from transformer.transformer_restapi import transform

        transform_event = {
            "mapping": {"id": ".inputId"},
            "input_payload": {"inputId": 123}
        }

        result = transform(transform_event, LambdaContext)

        assert result['statusCode'] == 200
        assert result['body'] == '{"id": 123}'

    def test_transform_malformed_payload(self):
        from transformer.transformer_restapi import transform

        transform_event = {
            "mapping": {"id": "inputId"},
            "input_payload": {"inputId": 123}
        }

        result = transform(transform_event, LambdaContext)

        assert result['statusCode'] == 400
    
    def test_transform_missing_payload(self):
        from transformer.transformer_restapi import transform

        transform_event = {
            "mapping": {"id": "inputId"}
        }

        result = transform(transform_event, LambdaContext)

        assert result['statusCode'] == 400
