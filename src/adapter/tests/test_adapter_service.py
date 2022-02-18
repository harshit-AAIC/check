import os
import json
from unittest.mock import patch, Mock

import unittest
import uuid
import datetime

from moto import mock_dynamodb2
import boto3
from aws_lambda_powertools import Logger

from adapter.adapter_service import AdapterService
from common.constant import DATE_FORMAT

logger = Logger(service="docuphase-ig-adapter")

@mock_dynamodb2
class AdapterRestApiTest(unittest.TestCase):
    def setUp(self):
      """
      Create database resource and mock table
      """
      os.environ['BASE_URL'] = "https://TSTDRV1667270.suitetalk.api.netsuite.com/services/rest"
      os.environ['AWS_REGION'] = "us-east-1"
      os.environ['ADAPTER_TABLE'] = "adapter-table"
      os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'] = 'auth_config_table'
      os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'] = 'oauth_authenticator_table'
      os.environ['ORACLE_NETSUITE_BASE_URL'] = "https://TSTDRV1667270.suitetalk.api.netsuite.com"
      os.environ['DISABLE_CORS'] = "True"
      self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
      self.dynamodb1 = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
      self.dynamodb2 = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
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
      self.table1 = self.dynamodb1.create_table(
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
      self.table2 = self.dynamodb2.create_table(
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
      self.table.delete()
      self.dynamodb=None
      self.table1.delete()
      self.dynamodb1=None
      self.table2.delete()
      self.dynamodb2=None

    def test_get_all_adapter_list(self):
        get_payload = {
        "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
        "name": "Oracle Adapter",
        "status": "Created",
        "type": "",
        "list_of_actions": [ {
            "name": "create purchase order to vendor bill",
            "input_attributes" : {
                "type": "object",
                "properties": {
                    "entityid" : { "type": "number", "description": "this is entity id" },
                    "companyname": { "type": "string", "description": "this is companyname " },
                    "subsidiary": {
                        "type": "object",
                        "properties": {
                            "id" : {"type": "number", "description": "this is id " }
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
                "input_attributes" : {
                    "type": "object",
                    "properties": {
                        "entityid" : { "type": "number", "description": "this is entity id" },
                        "companyname": { "type": "string", "description": "this is companyname " },
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id" : {"type": "number", "description": "this is id " }
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname"]
                },
                "function_name": "create_purchase_order"
                }
        ]
    }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)
        table.put_item(Item=item)
        adapter_service = AdapterService('91b42ce6-25b6-11ec-9003-1e80801e9786')

        result = adapter_service.get_all_adapter_list()
        assert len(result['Items']) > 0


    def test_get_all_adapter_list_is_empty(self):   
        adapter_service = AdapterService('91b42ce6-25b6-11e')

        result = adapter_service.get_all_adapter_list()
        assert result is None

    def test_get_adapter_action_by_id_found(self):
        get_payload = {
        "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
        "name": "Oracle Adapter",
        "status": "Created",
        "type": "",
        "list_of_actions": [ {
            "name": "create purchase order to vendor bill",
            "input_attributes" : {
                "type": "object",
                "properties": {
                    "entityid" : { "type": "number", "description": "this is entity id" },
                    "companyname": { "type": "string", "description": "this is companyname " },
                    "subsidiary": {
                        "type": "object",
                        "properties": {
                            "id" : {"type": "number", "description": "this is id " }
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
                "input_attributes" : {
                    "type": "object",
                    "properties": {
                        "entityid" : { "type": "number", "description": "this is entity id" },
                        "companyname": { "type": "string", "description": "this is companyname " },
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id" : {"type": "number", "description": "this is id " }
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname"]
                },
                "function_name": "create_purchase_order"
                }
        ]
    }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)
        adapter_service = AdapterService('91b42ce6-25b6-11ec-9003-1e80801e9786')
        result = adapter_service.get_adapter_action_details_by_id()
        assert result['ResponseMetadata']['HTTPStatusCode'] == 200

    def test_get_adapter_action_by_id_adapter_not_found(self):
        get_payload = {
        "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
        "name": "Oracle Adapter",
        "status": "Created",
        "type": "",
        "list_of_actions": [ {
            "name": "create purchase order to vendor bill",
            "input_attributes" : {
                "type": "object",
                "properties": {
                    "entityid" : { "type": "number", "description": "this is entity id" },
                    "companyname": { "type": "string", "description": "this is companyname " },
                    "subsidiary": {
                        "type": "object",
                        "properties": {
                            "id" : {"type": "number", "description": "this is id " }
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
                "input_attributes" : {
                    "type": "object",
                    "properties": {
                        "entityid" : { "type": "number", "description": "this is entity id" },
                        "companyname": { "type": "string", "description": "this is companyname " },
                        "subsidiary": {
                            "type": "object",
                            "properties": {
                                "id" : {"type": "number", "description": "this is id " }
                            },
                            "required": ["id"]
                        }
                    },
                    "required": ["entityid", "companyname"]
                },
                "function_name": "create_purchase_order"
                }
        ]
    }

        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)
        adapter_service = AdapterService('','create vendor bill')
        result = adapter_service.get_adapter_action_details_by_id()
        assert result == None


    def test_get_adapter_type_by_id(self):
        get_payload = {
        "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
        "name": "Oracle Adapter",
        "status": "Created",
        "type": "oracleNetsuite",
        "list_of_actions": [ {
            "name": "create purchase order to vendor bill",
            "input_attributes" : {
                "type": "object",
                "properties": {
                    "entityid" : { "type": "number", "description": "this is entity id" },
                    "companyname": { "type": "string", "description": "this is companyname " },
                    "subsidiary": {
                        "type": "object",
                        "properties": {
                            "id" : {"type": "number", "description": "this is id " }
                        },
                        "required": ["id"]
                    }
                },
                "required": ["entityid", "companyname", "subsidiary"]
            },
            "function_name": "create_purchase_order_to_vendor_bill"
            }
        ],
        "which_auth_mechanism" : "OAuth2",
        "what_auth_id" : '1234-abcd-5678-ghty'
    }

        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)
        adapter_service = AdapterService('91b42ce6-25b6-11ec-9003-1e80801e9786')
        result = adapter_service.get_adapter_type_by_id()
        assert result == 'oracleNetsuite'



    def test_get_adapter_type_by_id_not_found(self):
        get_payload = {
        "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
        "name": "Oracle Adapter",
        "status": "Created",
        "type": "oracleNetsuite",
        "list_of_actions": [ {
            "name": "create purchase order to vendor bill",
            "input_attributes" : {
                "type": "object",
                "properties": {
                    "entityid" : { "type": "number", "description": "this is entity id" },
                    "companyname": { "type": "string", "description": "this is companyname " },
                    "subsidiary": {
                        "type": "object",
                        "properties": {
                            "id" : {"type": "number", "description": "this is id " }
                        },
                        "required": ["id"]
                    }
                },
                "required": ["entityid", "companyname", "subsidiary"]
            },
            "function_name": "create_purchase_order_to_vendor_bill"
            }
        ],
        "which_auth_mechanism" : "OAuth2",
        "what_auth_id" : '1234-abcd-5678-ghty'
    }
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['ADAPTER_TABLE'])
        event_str = json.dumps(get_payload)
        item = json.loads(event_str)
        table.put_item(Item=item)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786')
        result = adapter_service.get_adapter_type_by_id()
        assert result is None

    @patch('requests.post')
    def test_get_oracle_adapter_object_and_call_adapter_action_for_create_customer(self, mocked_post):
        mocked_post.return_value = Mock(status_code=204)
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','create_customer', str(uuid.uuid1()))
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', request_json, '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 201

    @patch('requests.post')
    def test_get_oracle_adapter_object_and_call_adapter_action_for_create_customer_failed(self,mocked_post):
        mocked_post.return_value = Mock(status_code=403,
                                        text = {"type":"https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1","title":"Bad Request","status":400,"o:errorDetails":[{"detail":"Invalid record instance identifier '000'. Provide a valid record instance ID.","o:errorUrl":"/services/rest/record/v1/customer/000","o:errorCode":"INVALID_ID"}]})
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','create_customer', str(uuid.uuid1()) )
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', request_json, '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 403

    @patch('requests.get')
    def test_get_oracle_adapter_object_and_call_adapter_action_for_get_customer(self, mocked_get):
        mocked_get.return_value = Mock(status_code=201)
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','get_customer', str(uuid.uuid1()))
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite','123', '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 201

    @patch('requests.get')
    def test_get_oracle_adapter_object_and_call_adapter_action_for_get_customer_failed(self,mocked_get):
        mocked_get.return_value = Mock(status_code=400,
                                        text = {"type":"https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1","title":"Bad Request","status":400,"o:errorDetails":[{"detail":"Invalid record instance identifier '000'. Provide a valid record instance ID.","o:errorUrl":"/services/rest/record/v1/customer/000","o:errorCode":"INVALID_ID"}]})
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','get_customer', str(uuid.uuid1()) )
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', '000', '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 400

    @patch('requests.get')
    @patch('requests.post')
    def test_get_oracle_adapter_object_and_call_adapter_action_token_expired(self,mocked_post, mocked_get):
        mocked_get.return_value = Mock(status_code=401,
                                       text = {"type":"https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1","title":"Bad Request","status":400,"o:errorDetails":[{"detail":"Invalid record instance identifier '000'. Provide a valid record instance ID.","o:errorUrl":"/services/rest/record/v1/customer/000","o:errorCode":"INVALID_ID"}]})
        mocked_post.return_value = Mock(status_code=200, text= '{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "0",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id' : '12hdjgh-hddvfvdvfvdf-gggg',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret' : 'ghjklouytedcssnbvx',
            'callback_uri' : 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope' : 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url':'https://1234.netsuite.com/v1/token'
            
        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','get_customer', str(uuid.uuid1()) )
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', '000', '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 401

    @patch('requests.get')
    @patch('requests.post')
    def test_get_oracle_adapter_object_and_call_adapter_action_token_update_failed(self,mocked_post, mocked_get):
        mocked_get.return_value = Mock(status_code=401,
                                        text = {"type":"https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1","title":"Bad Request","status":400,"o:errorDetails":[{"detail":"Invalid record instance identifier '000'. Provide a valid record instance ID.","o:errorUrl":"/services/rest/record/v1/customer/000","o:errorCode":"INVALID_ID"}]})
        mocked_post.return_value = Mock(status_code=403, text= '{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "-1",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id' : '12hdjgh-hddvfvdvfvdf-gggg',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret' : 'ghjklouytedcssnbvx',
            'callback_uri' : 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope' : 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url':'https://1234.netsuite.com/v1/token'
            
        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','get_customer', str(uuid.uuid1()) )
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', '000', '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 403

    @patch('requests.get')
    def test_get_oracle_adapter_object_and_call_adapter_action_token_update_auth_config_not_found(self, mocked_get):
        mocked_get.return_value = Mock(status_code=401,
                                        text = {"type":"https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.1","title":"Bad Request","status":400,"o:errorDetails":[{"detail":"Invalid record instance identifier '000'. Provide a valid record instance ID.","o:errorUrl":"/services/rest/record/v1/customer/000","o:errorCode":"INVALID_ID"}]})
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "-1",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id' : '12hdjgh-hddvfvdvfvdf-gg',
            'mechanism': 'OAuth2',
            'client_id': '12234fdgsgd',
            'client_secret' : 'ghjklouytedcssnbvx',
            'callback_uri' : 'https://google.com',
            'token_url': 'https://1234.netsuite.com/v1/token',
            'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
            'scope' : 'rest_webservices',
            'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
            'response_type': 'code',
            'refresh_token_url':'https://1234.netsuite.com/v1/token'
            
        }
        table = dynamodb.Table(os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])
        event_str = json.dumps(auth_config)
        item = json.loads(event_str)
        table.put_item(Item=item)
        
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','get_customer', str(uuid.uuid1()) )
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', '000', '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 404


    def test_get_oracle_adapter_object_and_call_adapter_action_for_no_action_found(self):
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','create_purchase', str(uuid.uuid1()) )
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        result = adapter_service.get_adapter_object_and_call_adapter_action('oracleNetsuite', request_json, '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 404


    def test_get_microsoftgp_adapter_object_and_call_adapter_action_for_customer(self):
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','create_customer', str(uuid.uuid1()) )
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        result = adapter_service.get_adapter_object_and_call_adapter_action('microsoftGp', request_json, '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result['statusCode'] == 201


    def test_get_adapter_object_and_call_adapter_create_action_for_wrong_adapter_type(self):
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','create_customer', str(uuid.uuid1()) )
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        result = adapter_service.get_adapter_object_and_call_adapter_action('microsoftGpOracle', request_json, '12hdjgh-hddvfvdvfvdf-gggg', '12hdjgh-hddvfvdvfvdf-gggg')
        assert result is None


    def test_get_adapter_object_and_call_adapter_action_with_token_not_found(self):
        adapter_service = AdapterService('6666666-25b6-11ec-9003-1e80801e9786','create_customer', str(uuid.uuid1()) )
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        oauth2_payload['updated_at'] =  datetime.datetime.utcnow().strftime(DATE_FORMAT)
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        result = adapter_service.get_adapter_object_and_call_adapter_action('microsoftGp', request_json, '12hdjgh-hddvfvdvfvdf', '12hdjgh-hddvfvdvfvdf')
        assert result['statusCode'] == 404
