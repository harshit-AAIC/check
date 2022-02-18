import os
import json
import unittest
import boto3
import pytest
import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from unittest.mock import patch, Mock
from moto import mock_dynamodb2
from common.constant import DATE_FORMAT


logger = Logger()


@mock_dynamodb2
class FlowRestApitest(unittest.TestCase):

    """This class contains all Rest api Test cases"""

    def setUp(self):
        """
        Create database resource and mock table
        """
        os.environ['AWS_REGION'] = "us-east-1"
        os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'] = "docuphase-ig-adapter-oauth2-config-dev"
        os.environ['DISABLE_CORS'] = "True"
        self.dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        self.oauth_table = self.dynamodb.create_table(
            TableName=os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'],
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
        self.oauth_table.delete()
        self.dynamodb = None

    def test_create_ok(self):
        from adapter.adapter_oauth_config_restapi import create
        create_event = {'body': '{ "adapter_id":"sample", "client_id":"sample", "client_secret":"sample", "callback_uri": "sample", "redirect_uri": "sample", "token_url":"sample", "authorize_url": "sample", "scope": "sample", "state": "sample", "response_type":"sample", "refresh_token_url": "sample"}',
                        'httpMethod': 'POST', 'headers': {'origin': "*"}}
        result = create(create_event, LambdaContext)
        assert result["statusCode"] == 200
        assert result["body"] is not None

    def test_create_parsing_fail(self):
        from adapter.adapter_oauth_config_restapi import create
        create_parsing_fail = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                               'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_parsing_fail, LambdaContext)

    def test_get_ok(self):
        from adapter.adapter_oauth_config_restapi import create, get
        create_event = {'body': '{ "adapter_id":"sample", "client_id":"sample", "client_secret":"sample", "callback_uri": "sample", "redirect_uri": "sample", "token_url":"sample", "authorize_url": "sample", "scope": "sample", "state": "sample", "response_type":"sample", "refresh_token_url": "sample"}',
                        'httpMethod': 'GET', 'headers': {'origin': "*"}}
        result = create(create_event, LambdaContext)
        body = json.loads(result['body'])
        auth_id = body['id']
        get_event = {'body': "null", "pathParameters": {
            "id": auth_id}, 'httpMethod': 'POST', 'headers': {'origin': "*"}}
        response = get(get_event,LambdaContext)
        assert response['statusCode'] == 201

    def test_config_not_found(self):
        from adapter.adapter_oauth_config_restapi import create, get
        get_event = {'body': "null", "pathParameters": {
            "id": "sample"}, 'httpMethod': 'GET', 'headers': {'origin': "*"}}
        response = get(get_event,LambdaContext)
        assert response['statusCode'] == 404
