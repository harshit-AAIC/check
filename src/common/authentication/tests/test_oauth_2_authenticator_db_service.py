import json
import os
import uuid
from unittest.mock import patch, Mock
import unittest
import datetime
import boto3

from moto import mock_dynamodb2
from common.authentication.OAuth2_authenticator_db_service import OAuth2AuthenticatorDBService

NOT_FOUND_RESPONSE = {
    'statusCode': 404,
    'body': json.dumps('Item not Found')
}


adapter_payload = {
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
            }
        ],
        "which_auth_mechanism" : "OAuth2",
        "what_auth_id" : '1234-abcd-5678-ghty'
    }

@mock_dynamodb2
class OAuthAutheticatorDBServiceTest(unittest.TestCase):

    def setUp(self):
        """
        Create database resource and mock table
        """
        os.environ['AWS_REGION'] = "us-east-1"
        os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'] = 'oauth_authenticator_table'
        os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'] = 'auth_config_table'
        os.environ['ADAPTER_TABLE'] = "adapter-table"
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.dynamodb1 = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.dynamodb2 = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.table = self.dynamodb.create_table(
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

    def test_add_oauth2(self):
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "expires_in" : "3600",
        "token_type" : "Bearer",
        }
        oauth2db_obj = OAuth2AuthenticatorDBService(str(uuid.uuid1()))
        response = oauth2db_obj.add_access_token(oauth2_payload)
        assert response['statusCode'] == 201


    def test_get_oauth2_token(self):
        oauth2_payload = {
        "access_token" : "thisisaccesstokenstring",
        "refresh_token" : "thisisrefrestokenstring",
        "access_token_expiry_time" : "3600",
        "refresh_token_expiry_time" : "55000",
        "token_type" : "Bearer"
        }
        oauth2_payload['id'] = "12hdjgh-hddvfvdvfvdf-gggg"
        oauth2_payload['created_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        oauth2_payload['updated_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        oauth2db_obj = OAuth2AuthenticatorDBService('12hdjgh-hddvfvdvfvdf-gggg')
        response = oauth2db_obj.get_oauth2_by_id()
        assert response['statusCode'] == 201
        assert response['Item']['id'] == '12hdjgh-hddvfvdvfvdf-gggg'
        assert response['Item']['access_token'] == 'thisisaccesstokenstring'

    def test_get_oauth2_token_not_found(self):
        oauth2db_obj = OAuth2AuthenticatorDBService('12hdjgh-hddvfvdvfvdf-gggg')
        response = oauth2db_obj.get_oauth2_by_id()
        assert response['statusCode'] == NOT_FOUND_RESPONSE['statusCode']

    def test_update_ok(self):
        update_event = {
            "id": "91b42ce6-25b6-11ec-9003-1e80801e9786",
            "access_token" : "thisisaccesstokenstring",
            "refresh_token" : "thisisrefrestokenstring",
            "access_token_expiry_time" : "3600",
            "refresh_token_expiry_time" : "55000",
            "token_type" : "Bearer"
        }
        oauth2db_obj = OAuth2AuthenticatorDBService('91b42ce6-25b6-11ec-9003-1e80801e9786')
        result = oauth2db_obj.update_oauth2(update_event)
        assert result['statusCode'] == 201
        assert result['body']['id'] == '91b42ce6-25b6-11ec-9003-1e80801e9786'

    def test_update_item_is_not_present(self):
        oauth2_payload = {
            "id": "12hdjgh-hddvfvdvfvdf-gggg",
            "access_token" : "thisisaccesstokenstring",
            "refresh_token" : "thisisrefrestokenstring",
            "access_token_expiry_time" : "3600",
            "refresh_token_expiry_time" : "55000",
            "token_type" : "Bearer"
            }
        oauth2_payload['created_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        oauth2_payload['updated_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        update_event = {
            "id": "12hdjgh-hddvfvdvfvdf-gggg",
            "access_token" : "thisisaccesstokenstring",
            "refresh_token" : "thisisrefrestokenstring",
            "access_token_expiry_time" : "3600",
            "refresh_token_expiry_time" : "55000",
            "token_type" : "Bearer"
        }
        oauth2db_obj = OAuth2AuthenticatorDBService('12hdjgh-hddvfvdvfvdf-gggg')
        result = oauth2db_obj.update_oauth2(update_event)
        assert result['statusCode'] == 201
        assert result['body']['id'] == '12hdjgh-hddvfvdvfvdf-gggg'

    @patch('requests.post')
    def test_update_access_token_ok(self, mocked_post):
        mocked_post.return_value = Mock(status_code=200, text= '{"access_token": \
                "updatedtoken","refresh_token":"updated_token", \
                    "expires_in":"3600","token_type":"Bearer"}')
        
        oauth2_payload = {
            "id": "12hdjgh-hddvfvdvfvdf-gggg",
            "access_token" : "thisisaccesstokenstring",
            "refresh_token" : "thisisrefrestokenstring",
            "access_token_expiry_time" : "3600",
            "refresh_token_expiry_time" : "55000",
            "token_type" : "Bearer"
            }
        oauth2_payload['created_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        oauth2_payload['updated_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id' : '1234-abcd-5678-ghty',
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
        
        oauth2db_obj = OAuth2AuthenticatorDBService('12hdjgh-hddvfvdvfvdf-gggg')
        res = oauth2db_obj.update_access_token(auth_config, 'thisisrefrestokenstring')
        assert res['body']['access_token'] == 'updatedtoken'
        assert res['statusCode'] == 201

    @patch('requests.post')
    def test_update_access_token_failed(self, mocked_post):
        mocked_post.return_value = Mock(status_code=403, text= '{"access_token": \
                "updatedtoken","refresh_token":"updated_token", \
                    "expires_in":"3600","token_type":"Bearer"}')
        
        oauth2_payload = {
            "id": "12hdjgh-hddvfvdvfvdf-gggg",
            "access_token" : "thisisaccesstokenstring",
            "refresh_token" : "thisisrefrestokenstring",
            "access_token_expiry_time" : "3600",
            "refresh_token_expiry_time" : "55000",
            "token_type" : "Bearer"
            }
        oauth2_payload['created_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        oauth2_payload['updated_at'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)        
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        table = dynamodb.Table(os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])
        
        table.put_item(Item=oauth2)
        dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        auth_config = {
            'id' : '1234-abcd-5678-ghty',
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
        
        oauth2db_obj = OAuth2AuthenticatorDBService('12hdjgh-hddvfvdvfvdf-gggg')
        res = oauth2db_obj.update_access_token(auth_config, 'thisisrefrestokenstring')
        assert res['statusCode'] == 403
