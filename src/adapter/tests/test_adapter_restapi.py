import os
import json
import pytest
import unittest
from moto import mock_dynamodb2
from unittest.mock import patch, Mock
import boto3

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import ValidationError


logger = Logger(service="docuphase-ig-adapter")


@mock_dynamodb2
class AdapterRestApiTest(unittest.TestCase):
    def setUp(self):
        """
        Create database resource and mock table
        """
        os.environ['AWS_REGION'] = "us-east-1"
        os.environ['ADAPTER_TABLE'] = "adapter-table"
        os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'] = 'auth_config_table'
        os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'] = 'oauth_authenticator_table'
        os.environ['DISABLE_CORS'] = "True"
        self.dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        self.dynamodb1 = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        self.dynamodb2 = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        self.table = self.dynamodb.create_table(
            TableName=os.environ['ADAPTER_TABLE'],
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
        self.table1 = self.dynamodb.create_table(
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
        self.table2 = self.dynamodb.create_table(
            TableName=os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'],
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
        self.dynamodb = None
        self.table1.delete()
        self.dynamodb1 = None
        self.table2.delete()
        self.dynamodb2 = None

    def test_create_ok(self):
        from adapter.adapter_restapi import create
        create_event = {'body': '{"name": "Oracle Adapter", "status": "Created", "type": "",'
                        '"list_of_actions": [ {"name": "create purchase order to vendor bill", "input_attributes" : {"type": "object", "properties": {"entityid" : { "type": "number", "description": "this is entity id" }, "companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname", "subsidiary"]},"function_name": "create_purchase_order_to_vendor_bill"},{"name": "create purchase order","input_attributes" : {"type": "object","properties": {"entityid" : { "type": "number", "description": "this is entity id" },"companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname"]},"function_name": "create purchase order" }],"which_auth_mechanism" : "OAuth2", "what_auth_id" : "eeeeee-1234-ggggg"}',
                        'httpMethod': 'POST'}

        result = create(create_event,
                        LambdaContext)
        assert result['statusCode'] == 201

    def test_create_name_validation(self):
        with pytest.raises(KeyError):
            from adapter.adapter_restapi import create
            create_event = {'body': '{"status": "Created", "type": "", "list_of_actions": [ {"name": "create purchase order to vendor bill", "input_attributes" : {"type": "object", "properties": {"entityid" : { "type": "number", "description": "this is entity id" }, "companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname", "subsidiary"]},"function_name": "create_purchase_order_to_vendor_bill"},{"name": "create purchase order","input_attributes" : {"type": "object","properties": {"entityid" : { "type": "number", "description": "this is entity id" },"companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname"]},"function_name": "create purchase order" }]}',
                            'httpMethod': 'POST'}

            result = create(create_event,
                            LambdaContext)

    # # Test get

    def test_get_ok(self):
        from adapter.adapter_restapi import get
        get_payload = {
            "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
            "name": "Oracle Adapter",
            "status": "Created",
            "type": "",
            "list_of_actions": [{
                "name": "create purchase order to vendor bill",
                "input_attributes": {
                    "type": "object",
                    "properties": {
                        "entityid": {"type": "number", "description": "this is entity id"},
                        "companyname": {"type": "string", "description": "this is companyname "},
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number", "description": "this is id "}
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname", "subsidiary"]
                },
                "function_name": "create_purchase_order_to_vendor_bill"
            },
                {
                "name": "create purchase order",
                "input_attributes": {
                    "type": "object",
                    "properties": {
                        "entityid": {"type": "number", "description": "this is entity id"},
                        "companyname": {"type": "string", "description": "this is companyname "},
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number", "description": "this is id "}
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname"]
                },
                "function_name": "create_purchase_order"
            }
            ],
            "which_auth_mechanism": "OAuth2",
            "what_auth_id": '1234-abcd-5678-ghty'
        }
        dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)

        get_event = {'httpMethod': 'GET', 'pathParameters': {
            'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'}}
        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 201

    def test_get_list_of_action_missing(self):
        with pytest.raises(ValidationError):
            from adapter.adapter_restapi import get
            get_payload = {
                "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
                "name": "Oracle Adapter",
                "status": "Created",
                "type": "oracle",
            }
            dynamodb = boto3.resource(
                'dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)

            get_event = {'httpMethod': 'GET', 'pathParameters': {
                'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'}}
            result = get(get_event, LambdaContext)

    def test_get_not_found(self):
        from adapter.adapter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {
            'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'}}
        result = get(get_event,  LambdaContext)

        assert result['statusCode'] == 404

    def test_get_pathparameter_is_none(self):
        from adapter.adapter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': None}}

        result = get(get_event, LambdaContext)
        assert result['statusCode'] == 404

    def test_get_pathparameter_is_empty(self):
        from adapter.adapter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': ''}}

        result = get(get_event, LambdaContext)
        assert result['statusCode'] == 404

    def test_get_pathparameter_is_missing(self):
        from adapter.adapter_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {}}
        with pytest.raises(KeyError):
            result = get(get_event, LambdaContext)
        # assert result['statusCode'] == 404

    # List

    def test_list_ok(self):
        from adapter.adapter_restapi import get_list
        get_payload = {
            "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
            "name": "Oracle Adapter",
            "status": "Created",
            "type": "",
            "list_of_actions": [{
                "name": "create purchase order to vendor bill",
                "input_attributes": {
                    "type": "object",
                    "properties": {
                        "entityid": {"type": "number", "description": "this is entity id"},
                        "companyname": {"type": "string", "description": "this is companyname "},
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number", "description": "this is id "}
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname", "subsidiary"]
                },
                "function_name": "create_purchase_order_to_vendor_bill"
            },
                {
                "name": "create purchase order",
                "input_attributes": {
                    "type": "object",
                    "properties": {
                        "entityid": {"type": "number", "description": "this is entity id"},
                        "companyname": {"type": "string", "description": "this is companyname "},
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number", "description": "this is id "}
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname"]
                },
                "function_name": "create_purchase_order"
            }
            ],
            "which_auth_mechanism": "OAuth2",
            "what_auth_id": '1234-abcd-5678-ghty'
        }

        dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)
        table.put_item(Item=item)
        result = get_list(None, context=LambdaContext)

        assert result['statusCode'] == 201
        assert len(result['body']) > 2

    def test_list_validation_error(self):
        with pytest.raises(ValidationError):
            from adapter.adapter_restapi import get_list
            get_payload = {
                "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
                "name": "Oracle Adapter",
                "status": "Created",
                "type": ""
            }

            dynamodb = boto3.resource(
                'dynamodb', region_name=os.environ['AWS_REGION'])

            table = dynamodb.Table(os.environ['ADAPTER_TABLE'])

            event_str = json.dumps(get_payload)
            item = json.loads(event_str)

            table.put_item(Item=item)
            table.put_item(Item=item)

            get_list(None, context=LambdaContext)

    def test_get_authorization_url_not_found(self):
        from adapter.adapter_restapi import get_authorization_auth_url
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': '91b42ce6-25b6-11ec-9003-1e80801e9786'}}
        dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id': '1234-abcd-5678-ghty',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret': 'ghjklouytedcssnbvx',
            'callback_uri': 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope': 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url': 'https://1234.netsuite.com/v1/token'

        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        authorization_url_res = get_authorization_auth_url(
            event=get_event, context=LambdaContext)
        assert authorization_url_res is not None
        assert authorization_url_res['statusCode'] == 404

    def test_get_authorization_url_ok(self):
        from adapter.adapter_restapi import get_authorization_auth_url
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': '1234-abcd-5678-ghty'}}
        dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id': '1234-abcd-5678-ghty',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret': 'ghjklouytedcssnbvx',
            'callback_uri': 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope': 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url': 'https://1234.netsuite.com/v1/token'

        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        authorization_url_res = get_authorization_auth_url(
            event=get_event, context=LambdaContext)
        assert authorization_url_res['statusCode'] == 201

    @patch('requests.post')
    def test_get_access_token_ok(self, mocked_post):
        mocked_post.return_value = Mock(status_code=200, text='{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')
        from adapter.adapter_restapi import get_access_token_using_auth_code
        get_event = {'httpMethod': 'GET', 'body': '{"auth_code" : "thyujfddsss"}',
                     'pathParameters': {'id': '1234-abcd-5678-ghty'},
                     }
        dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id': '1234-abcd-5678-ghty',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret': 'ghjklouytedcssnbvx',
            'callback_uri': 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope': 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url': 'https://1234.netsuite.com/v1/token'

        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        authorization_url_res = get_access_token_using_auth_code(
            event=get_event, context=LambdaContext)
        assert authorization_url_res is not None
        assert authorization_url_res['statusCode'] == 201

    @patch('requests.post')
    def test_get_access_token_failed(self, mocked_post):
        mocked_post.return_value = Mock(status_code=403, text='{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')
        from adapter.adapter_restapi import get_access_token_using_auth_code
        get_event = {'httpMethod': 'GET', 'body': '{"auth_code" : "thyujfddsss"}',
                     'pathParameters': {'id': '1234-abcd-5678-ghty'},
                     }
        dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id': '1234-abcd-5678-ghty',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret': 'ghjklouytedcssnbvx',
            'callback_uri': 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope': 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url': 'https://1234.netsuite.com/v1/token'

        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        authorization_url_res = get_access_token_using_auth_code(
            event=get_event, context=LambdaContext)
        assert authorization_url_res is not None
        assert authorization_url_res['statusCode'] == 403
