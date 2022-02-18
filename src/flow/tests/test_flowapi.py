import os
import json
import unittest
import boto3
import pytest
import datetime
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from unittest.mock import patch, Mock
from adapter.adapter_restapi import create as create_adapter
from filter.filter_restapi import create as create_filter
from transformer.transformer_restapi import create as create_transformer
from flow.flow import Flow
from flow.flow_execution_service import FlowExecutionService
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
        os.environ['FLOW_TABLE'] = "Flow-table"
        os.environ['ADAPTER_TABLE'] = "adapter-table"
        os.environ['FILTER_TABLE'] = "filter-table"
        os.environ['TRANSFORMER_TABLE'] = "transformer-table"
        os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'] = 'oauth_authenticator_table'
        os.environ['FLOW_EXECUTION_TABLE'] = 'flow_execution_info_table'
        os.environ['ORACLE_NETSUITE_BASE_URL'] = "https://TSTDRV1667270.suitetalk.api.netsuite.com"
        os.environ['DISABLE_CORS'] = "True"
        self.dynamodb = boto3.resource(
            'dynamodb', region_name=os.environ['AWS_REGION'])
        self.flow_table = self.dynamodb.create_table(
            TableName=os.environ['FLOW_TABLE'],
            KeySchema=[
                {
                    'AttributeName': 'flow_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'flow_id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        self.adapter_table = self.dynamodb.create_table(
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
        self.filter_table = self.dynamodb.create_table(
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
        self.transformer_table = self.dynamodb.create_table(
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
        self.oauth2_authenticator_table = self.dynamodb.create_table(
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
        self.flow_execution_table = self.dynamodb.create_table(
            TableName=os.environ['FLOW_EXECUTION_TABLE'],
            KeySchema=[
                {
                    'AttributeName': 'execution_id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'execution_id',
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
        self.flow_table.delete()
        self.dynamodb = None
        self.adapter_table.delete()
        self.dynamodb = None
        self.filter_table.delete()
        self.dynamodb = None
        self.transformer_table.delete()
        self.dynamodb = None
        self.oauth2_authenticator_table.delete()
        self.dynamodb = None
        self.flow_execution_table.delete()
        self.dynamodb = None


    def test_create_ok(self):
        from flow.flow_restapi import create
        create_event = {'body': '{ "name": "sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png","flowstep":[{"order":"sample", "action_name":"create_customer", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                        'httpMethod': 'POST'}
        result = create(create_event, LambdaContext)
        assert result["statusCode"] == 201
        assert result["body"] is not None
        # now get the same flow using above id

    def test_create_without_filter_id(self):
        from flow.flow_restapi import create
        create_without_filter_id = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                                    'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_filter_id, LambdaContext)

    def test_create_with_null_filter_id(self):
        from flow.flow_restapi import create
        create_without_filter_id = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample", "filter_id":null, "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                                    'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_filter_id, LambdaContext)

    def test_create_without_adapter_id(self):
        from flow.flow_restapi import create
        create_without_adapter_id = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample", "before_transformer_id":"sample", "filter_id":"sample", "after_transformer_id":"sample"}]}',
                                     'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_adapter_id, LambdaContext)

    def test_create_with_null_adapter_id(self):
        from flow.flow_restapi import create
        create_without_adapter_id = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample", "before_transformer_id":"sample", "adapter_id": null, "filter_id":"sample", "after_transformer_id":"sample"}]}',
                                     'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_adapter_id, LambdaContext)

    def test_create_without_before_transformer_id(self):
        from flow.flow_restapi import create
        create_without_before_transformer_id = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample","adapter_id":"sample" , "filter_id":"sample", "after_transformer_id":"sample"}]}',
                                                'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_before_transformer_id, LambdaContext)

    def test_create_with_null_before_transformer_id(self):
        from flow.flow_restapi import create
        create_without_before_transformer_id = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample","adapter_id":"sample" , "filter_id":"sample", "after_transformer_id":"sample", "before_transformer_id":null}]}',
                                                'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_before_transformer_id, LambdaContext)

    def test_create_without_after_transformer_id(self):
        from flow.flow_restapi import create
        create_without_after_transformer_id = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "action_name":"sample","adapter_id":"sample" , "filter_id":"sample", "before_transformer_id":"sample"}]}',
                                               'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_after_transformer_id, LambdaContext)

    def test_create_with_null_after_transformer_id(self):
        from flow.flow_restapi import create
        create_without_after_transformer_id = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg","flowstep":[{"order":"sample", "action_name":"sample","adapter_id":"sample" , "filter_id":"sample", "before_transformer_id":"sample", "after_transformer_id":null}]}',
                                               'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(create_without_after_transformer_id, LambdaContext)

    def test_create_without_action_name(self):
        from flow.flow_restapi import create
        event_without_action_name = {'body': '{"id":"sample", "name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "flowstep":[{"order":"sample", "after_transformer_id":"sample", "adapter_id":"sample" , "filter_id":"sample", "before_transformer_id":"sample"}]}',
                                     'httpMethod': 'POST'}
        with pytest.raises(KeyError):
            create(event_without_action_name, LambdaContext)

    def test_flow_name_already_exists(self):
        from flow.flow_restapi import create
        create_event = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png", "flowstep":[{"order":"sample", "action_name":"create_customer", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                        'httpMethod': 'POST'}
        create(create_event, LambdaContext)
        create_event_flow_name_already_exists = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg","adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png", "flowstep":[{"order":"sample", "action_name":"create_customer", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                                                 'httpMethod': 'POST'}
        result = create(create_event_flow_name_already_exists, LambdaContext)
        assert result["statusCode"] == 403


    # # #### Get

    def test_get_ok(self):
        from flow.flow_restapi import get, create
        create_event = {'body': '{"name":"sample", "desc":"sample", "status":"sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png", "flowstep":[{"order":"sample", "action_name":"create_customer", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"} ] }',
                        'httpMethod': 'POST', 'pathParameters': {"id": "123"} }
        json_response = create(create_event, LambdaContext)
        response = json.loads(json_response.get("body"))
        flow_id = response["flow_id"]
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': flow_id}}
        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 200

    def test_get_not_found(self):
        from flow.flow_restapi import get

        get_event = {'httpMethod': 'GET', 'pathParameters': {'id': '123'}}
        result = get(get_event, LambdaContext)

        assert result['statusCode'] == 404

    def test_get_credentials_not_found(self):
        from flow.flow_restapi import get, create

        create_event = {'body': '{"name":"sample", "desc":"sample", "status":"sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png", "flowstep":[{"order":"sample", "action_name":"create_customer", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                        'httpMethod': 'POST'}
        create(create_event, LambdaContext)

        get_event_with_id_None = {'httpMethod': 'GET',
                                  'pathParameters': {'flow_id': None}}
        with pytest.raises(KeyError):
            result = get(get_event_with_id_None, LambdaContext)
        # assert result['statusCode'] == 401

    # # #### List

    def test_list_ok(self):
        from flow.flow_restapi import get_list
        list_event = {'httpMethod': 'GET', 'queryStringParameters': {
            'limit': 10, 'pagination_token': "GAYD"}}
        result = get_list(list_event, LambdaContext)


        assert result['statusCode'] == 200

    def test_no_queryStringParameters(self):
        from flow.flow_restapi import get_list

        list_event = {'httpMethod': 'GET', 'queryStringParameters': None}
        result = get_list(list_event, LambdaContext)

        assert result['statusCode'] == 200

    def test_invalid_queryStringParameters(self):
        from flow.flow_restapi import get_list
        list_event = {'httpMethod': 'GET', 'queryStringParameters': {
            'limit': 10, 'pagination_token': "GIYDAOBNGEYS2MBWKQYDAORQGA5DAMBOGAYDAKZQGAYDALBQ"}}
        result = get_list(list_event, LambdaContext)

        assert result['statusCode'] == 400

    # # #### Update

    def test_update_ok(self):
        from flow.flow_restapi import update

        update_event = {'body': '{"name":"sample", "desc":"sample", "status":"sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png","flowstep":[{"order":"sample", "action_name":"sample", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                        'pathParameters': {'id': '123'},
                        'httpMethod': 'PUT'}
        result = update(update_event, LambdaContext)

        assert result['statusCode'] == 200

    def test_update_with_none_flow_id(self):
        from flow.flow_restapi import update

        update_event = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg","flowstep":[{"order":"sample", "action_name":"sample", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                        'pathParameters': {'id': None},
                        'httpMethod': 'PUT'}
        with pytest.raises(ValueError):
            update(update_event, LambdaContext)


    def test_update_with_no_pathparameter(self):
        from flow.flow_restapi import update

        update_event_without_pathParameter = {'body': '{"name":"sample", "desc":"sample", "status":"sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg","flowstep":[{"order":"sample", "action_name":"sample", "filter_id":"sample", "before_transformer_id":"sample", "adapter_id":"sample", "after_transformer_id":"sample"}]}',
                                              'httpMethod': 'PUT'}

        result = update(update_event_without_pathParameter, LambdaContext)
        assert result['statusCode'] == 404


    @patch('requests.post')
    def test_flow_process(self, mocked_post):
        mocked_post.return_value = Mock(status_code=204)
        from flow.flow_restapi import process, create

        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)

        # adapter_service = AdapterService()
        adapter_create_event = {'body': '{"name": "Oracle Adapter", "status": "Created", "type": "oracleNetsuite",'
                        '"list_of_actions": [ {"name": "create customer", "input_attributes" : {"type": "object", "properties": {"entityid" : { "type": "number", "description": "this is entity id" }, "companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname", "subsidiary"]},"function_name": "create customer"},{"name": "create purchase order","input_attributes" : {"type": "object","properties": {"entityid" : { "type": "number", "description": "this is entity id" },"companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname"]},"function_name": "create purchase order" }],"which_auth_mechanism" : "OAuth2", "what_auth_id" : "12hdjgh-hddvfvdvfvdf-gggg"}',
        'httpMethod': 'POST'}
        filter_create_event = {'body': '{"name": "CONDITION CONTAINS","status": "Created","filter_criteria": [{"key": "country", "value": "in","condition": "contains", "operator": ""}]}',
        'httpMethod': 'POST'}
        transformer_create_event = {'body':'{"name": "Oracle Transformer", "input_payload": {"S.No" : "1", "first name": "tests"}, "status": "Created", "mapping_payload": {"country_name": ".country", "subject_name": ".subject", "state_name": ".state", "city_name": ".city"} }', 
                                    'httpMethod': 'POST'}

        filter_create_response_str = create_filter(filter_create_event, LambdaContext)
        filter_id = json.loads(filter_create_response_str.get('body'))['id']

        transformer_create_response = create_transformer(transformer_create_event, LambdaContext)
        before_transformer_id = json.loads(transformer_create_response.get('body'))['id']

        adapter_create_response = create_adapter(adapter_create_event, LambdaContext)
        adapter_id = json.loads(adapter_create_response.get('body'))['id']
        flow_create_event = {'body': {"name": "sample", "desc": "sample", "status": "sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg","adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png","flowstep": [{"order": "sample", "action_name": "create_customer", "filter_id": filter_id, "before_transformer_id": before_transformer_id, "adapter_id": adapter_id, "after_transformer_id": "sample"}]},
                        'httpMethod': 'POST'}
        flow_create_event['body'] = json.dumps(flow_create_event['body'])
        logger.info(f"new event {flow_create_event}")
        json_flow_data = create(flow_create_event, LambdaContext)
        flow_body = json.loads(json_flow_data.get("body"))
        flow_id = flow_body["flow_id"]
        process_flow_event = {'httpMethod': 'PUT', 'pathParameters': {
            'id': flow_id}, 'body': '{"subject": "Hello, world!","country": "India", "state": "Maharashtra", "city": "Pune"}'}
        result = process(process_flow_event, LambdaContext)
        assert result['statusCode'] == 201

    def test_flow_process_with_filter_failed(self):
        from flow.flow_restapi import process, create
        filter_create_event = {'body': '{"name": "CONDITION CONTAINS","status": "Created","filter_criteria": [{"key": "country", "value": "TCS","condition": "contains", "operator": ""}]}',
        'httpMethod': 'POST'}

        filter_create_response_str = create_filter(filter_create_event, LambdaContext)
        filter_id = json.loads(filter_create_response_str.get('body'))['id']

        flow_create_event = {'body': {"name": "sample", "desc": "sample", "status": "sample", "auth_id":"12hdjgh-hddvfvdvfvdf-gggg","adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png","flowstep": [{"order": "sample", "action_name": "create_customer", "filter_id": filter_id, "before_transformer_id": "7ugdf-gdfggf", "adapter_id": "1234-yhts", "after_transformer_id": "sample"}]},
                        'httpMethod': 'POST'}
        flow_create_event['body'] = json.dumps(flow_create_event['body'])
        logger.info(f"new event {flow_create_event}")
        json_flow_data = create(flow_create_event, LambdaContext)
        flow_body = json.loads(json_flow_data.get("body"))
        flow_id = flow_body["flow_id"]
        process_flow_event = {'httpMethod': 'PUT', 'pathParameters': {
            'id': flow_id}, 'body': '{"subject": "Hello, world!","country": "India", "state": "Maharashtra", "city": "Pune"}'}
        result = process(process_flow_event, LambdaContext)
        assert result['statusCode'] == 400


    @patch('requests.post')
    def test_flow_process_failed(self, mocked_post):
        mocked_post.return_value = Mock(status_code=403,
                                        text = {"type":"https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1","title":"Bad Request","status":400,"o:errorDetails":[{"detail":"Invalid record instance identifier '000'. Provide a valid record instance ID.","o:errorUrl":"/services/rest/record/v1/customer/000","o:errorCode":"INVALID_ID"}]})
        from flow.flow_restapi import process, create

        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_create_event = {'body': '{"name": "Oracle Adapter", "status": "Created", "type": "oracleNetsuite",'
                        '"list_of_actions": [ {"name": "create customer", "input_attributes" : {"type": "object", "properties": {"entityid" : { "type": "number", "description": "this is entity id" }, "companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname", "subsidiary"]},"function_name": "create customer"},{"name": "create purchase order","input_attributes" : {"type": "object","properties": {"entityid" : { "type": "number", "description": "this is entity id" },"companyname": { "type": "string", "description": "this is companyname " }, "subsidiary": {"type": "object","properties": {"id" : {"type": "number", "description": "this is id " } },"required": ["id"]} },"required": ["entityid", "companyname"]},"function_name": "create purchase order" }],"which_auth_mechanism" : "OAuth2", "what_auth_id" : "12hdjgh-hddvfvdvfvdf-gggg"}',
        'httpMethod': 'POST'}
        filter_create_event = {'body': '{"name": "CONDITION CONTAINS","status": "Created","filter_criteria": [{"key": "country", "value": "in","condition": "contains", "operator": ""}]}',
        'httpMethod': 'POST'}
        transformer_create_event = {'body':'{"name": "Oracle Transformer", "input_payload": {"S.No" : "1", "first name": "tests"}, "status": "Created", "mapping_payload": {"country_name": ".country", "subject_name": ".subject", "state_name": ".state", "city_name": ".city"} }', 
                                    'httpMethod': 'POST'}

        filter_create_response_str = create_filter(filter_create_event, LambdaContext)
        filter_id = json.loads(filter_create_response_str.get('body'))['id']

        transformer_create_response = create_transformer(transformer_create_event, LambdaContext)
        before_transformer_id = json.loads(transformer_create_response.get('body'))['id']

        adapter_create_response = create_adapter(adapter_create_event, LambdaContext)
        adapter_id = json.loads(adapter_create_response.get('body'))['id']
        flow_create_event = {'body': {"name": "sample", "desc": "sample", "status": "sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png","flowstep": [{"order": "sample", "action_name": "create_customer", "filter_id": filter_id, "before_transformer_id": before_transformer_id, "adapter_id": adapter_id, "after_transformer_id": "sample"}]},
                        'httpMethod': 'POST'}
        flow_create_event['body'] = json.dumps(flow_create_event['body'])
        logger.info(f"new event {flow_create_event}")
        json_flow_data = create(flow_create_event, LambdaContext)
        flow_body = json.loads(json_flow_data.get("body"))
        flow_id = flow_body["flow_id"]
        process_flow_event = {'httpMethod': 'PUT', 'pathParameters': {
            'id': flow_id}, 'body': '{"subject": "Hello, world!","country": "India", "state": "Maharashtra", "city": "Pune"}'}
        result = process(process_flow_event, LambdaContext)
        assert result['statusCode'] == 403
    
    def test_get_sample_input_payload(self):
        from flow.flow_restapi import get_sample_input_payload, create
        transformer_create_event = {'body':'{"name": "Oracle Transformer", "input_payload": {"S.No" : "1", "first name": "tests"}, "status": "Created", "mapping_payload": {"country_name": ".country", "subject_name": ".subject", "state_name": ".state", "city_name": ".city"} }', 
                                    'httpMethod': 'POST'}
        transformer_create_response = create_transformer(transformer_create_event, LambdaContext)
        before_transformer_id = json.loads(transformer_create_response.get('body'))['id']
        flow_create_event = {'body': {"name": "sample", "desc": "sample", "status": "sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg","adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png", "flowstep": [{"order": "sample", "action_name": "create_customer", "filter_id": 'sample', "before_transformer_id": before_transformer_id, "adapter_id": "sample", "after_transformer_id": "sample"}]},
                        'httpMethod': 'POST'}
        flow_create_event['body'] = json.dumps(flow_create_event['body'])
        logger.info(f"new event {flow_create_event}")
        json_flow_data = create(flow_create_event, LambdaContext)
        flow_body = json.loads(json_flow_data.get("body"))
        flow_id = flow_body["flow_id"]
        process_flow_get_event = {'httpMethod': 'PUT', 'pathParameters': {
            'id': flow_id}}
        result = get_sample_input_payload(process_flow_get_event, LambdaContext)
        assert result['statusCode'] == 201

    def test_get_sample_input_payload_failed(self):
        from flow.flow_restapi import get_sample_input_payload, create
        transformer_create_event = {'body':'{"name": "Oracle Transformer", "input_payload": {"S.No" : "1", "first name": "tests"}, "status": "Created", "mapping_payload": {"country_name": ".country", "subject_name": ".subject", "state_name": ".state", "city_name": ".city"} }', 
                                    'httpMethod': 'POST'}
        transformer_create_response = create_transformer(transformer_create_event, LambdaContext)
        before_transformer_id = json.loads(transformer_create_response.get('body'))['id']
        flow_create_event = {'body': {"name": "sample", "desc": "sample", "status": "sample","auth_id":"12hdjgh-hddvfvdvfvdf-gggg", "adapter_img": "https://docuphase-cognito-service-dev-bucket.s3.amazonaws.com/oracle.png","flowstep": [{"order": "sample", "action_name": "create_customer", "filter_id": 'sample', "before_transformer_id": "random id", "adapter_id": "sample", "after_transformer_id": "sample"}]},
                        'httpMethod': 'POST'}
        flow_create_event['body'] = json.dumps(flow_create_event['body'])
        logger.info(f"new event {flow_create_event}")
        json_flow_data = create(flow_create_event, LambdaContext)
        flow_body = json.loads(json_flow_data.get("body"))
        flow_id = flow_body["flow_id"]
        process_flow_get_event = {'httpMethod': 'PUT', 'pathParameters': {
            'id': flow_id}}
        result = get_sample_input_payload(process_flow_get_event, LambdaContext)

        assert result['statusCode'] == 404
    
### Test Get execution list for flow
    def test_get_execution_list_ok(self):
        from flow.flow_restapi import get_flow_execution_list
        execution_payload = {"flow_id": "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                            "execution_id": "bc781544-6c58-11ec-9578-e66cceae7d28",
                            "status": "running"
                            }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['FLOW_EXECUTION_TABLE'])
        
        table.put_item(Item=execution_payload)
        flow_id = "bc773bce-6c58-11ec-9578-e66cceae7d28"
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': flow_id}}
        result = get_flow_execution_list(get_event, LambdaContext)
        assert result['statusCode'] == 200
        assert result["body"] is not None
    
    def test_get_execution_list_not_found(self):
        from flow.flow_restapi import get_flow_execution_list
        execution_payload = {"flow_id": "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                            "execution_id": "bc781544-6c58-11ec-9578-e66cceae7d28",
                            }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['FLOW_EXECUTION_TABLE'])
        
        table.put_item(Item=execution_payload)
        flow_id = "bc773bce-6c58-11ec-9578-e66cceae7d2"
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': flow_id}}
        result = get_flow_execution_list(get_event, LambdaContext)
        assert result['statusCode'] == 404
    
    def test_get_execution_list_credentials_not_found(self):
        from flow.flow_restapi import get_flow_execution_list

        execution_payload = {"flow_id": "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                            "execution_id": "bc781544-6c58-11ec-9578-e66cceae7d28",
                            }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['FLOW_EXECUTION_TABLE'])
        
        table.put_item(Item=execution_payload)

        get_event_with_id_None = {'httpMethod': 'GET',
                                  'pathParameters': {'flow_id': None}}
        with pytest.raises(KeyError):
            get_flow_execution_list(get_event_with_id_None, LambdaContext)
    
    def test_create_flow_execution_parser_error(self):
        execution_payload = {"flow_id": "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                            "execution_id": "bc781544-6c58-11ec-9578-e66cceae7d28"
                            }
        flow_execution = FlowExecutionService("bc773bce-6c58-11ec-9578-e66cceae7d28", "bc773bce-6c58-11ec-9578-e66cceae7d28")
        with pytest.raises(KeyError):
            flow_execution.create_flow_execution(execution_payload)
    
    def test_get_execution_by_status(self):
        from flow.flow_restapi import get_execution_by_status
        execution_payload = {"flow_id": "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                            "execution_id": "bc781544-6c58-11ec-9578-e66cceae7d28",
                            "status" : 'success'
                            }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['FLOW_EXECUTION_TABLE'])
        
        table.put_item(Item=execution_payload)
        execution_payload['status'] ='success'
        
        table.put_item(Item=execution_payload)
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                     'status': "success"} }
        res =  get_execution_by_status(get_event, LambdaContext)
        assert res['statusCode'] == 200
        assert res["body"] is not None
    
    def test_get_execution_by_status_not_found(self):
        from flow.flow_restapi import get_execution_by_status
        execution_payload = {"flow_id": "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                            "execution_id": "bc781544-6c58-11ec-9578-e66cceae7d28",
                            "status" : 'success'
                            }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['FLOW_EXECUTION_TABLE'])
        
        table.put_item(Item=execution_payload)
        execution_payload['status'] ='failed'
        
        table.put_item(Item=execution_payload)
        get_event = {'httpMethod': 'GET',
                     'pathParameters': {'id': "bc773bce-6c58-11ec-9578-e66cceae7d28", 
                     'status': "success"} }
        res =  get_execution_by_status(get_event, LambdaContext)
        assert res['statusCode'] == 404
    
    def test_get_execution_by_status_raise_error(self):
        from flow.flow_restapi import get_execution_by_status
        get_event_with_id_None = {'httpMethod': 'GET',
                                  'pathParameters': {'flow_id': None}}
        with pytest.raises(KeyError):
            get_execution_by_status(get_event_with_id_None, LambdaContext)
