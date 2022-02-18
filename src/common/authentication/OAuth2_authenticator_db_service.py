""" This package saves  Oauth authenticator info in DB"""
import datetime
import json
import os
import uuid

import boto3
from aws_lambda_powertools import Logger
from common.constant import DATE_FORMAT

from authentication.OAuth2_authenticator_service import \
    OAuth2AuthenticatorService

NOT_FOUND_RESPONSE = {
    "statusCode": 404,
    "body": json.dumps('Item not Found'),
    "headers": {
        "Access-Control-Allow-Origin": "*"
    }
}

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
logger = Logger(service="docuphase-ig-oauth2")

""" Class for OAuth authentication DB service. """


class OAuth2AuthenticatorDBService:
    """Class init """

    def __init__(self, oauth_id, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource(
                'dynamodb', region_name=os.environ['AWS_REGION'])
        self.__id = oauth_id
        self.__current_timestamp = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        self.__table = dynamodb.Table(
            os.environ['OAUTH2_AUTHENTICATOR_DYNAMODB_TABLE'])

    def add_oauth2(self, oauth2_payload):
        """ Method for creating oauth2. """
        oauth2_payload['id'] = self.__id
        oauth2_payload['created_at'] = self.__current_timestamp
        oauth2_payload['updated_at'] = self.__current_timestamp
        payload_str = json.dumps(oauth2_payload)
        oauth2 = json.loads(payload_str)
        self.__table.put_item(Item=oauth2)
        response = {
            "statusCode": 201,
            "body": json.dumps(oauth2),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
        return response

    def get_oauth2_by_id(self):
        """ Method for fetching the oauth2 object using it's id. """
        result = self.__table.get_item(
            Key={
                'id': self.__id
            }
        )

        if result and 'Item' in result:
            response = {
                "statusCode": 201,
                "Item": result['Item']
            }
            return response
        logger.info(f"No oauth2 entry found with this id {self.__id}")
        return NOT_FOUND_RESPONSE

    def update_oauth2(self, oauth2_payload):
        """ Method for updating oauth2. """
        result = self.__table.update_item(
            Key={
                'id': self.__id
            },
            ExpressionAttributeNames={
                "#access_token": "access_token",
                "#access_token_expiry_time": "access_token_expiry_time",
            },
            ExpressionAttributeValues={
                ":access_token": oauth2_payload['access_token'],
                ":access_token_expiry_time": oauth2_payload['access_token_expiry_time'],
                ":updated_at": self.__current_timestamp
            },
            UpdateExpression="set #access_token=:access_token,"
                             "#access_token_expiry_time=:access_token_expiry_time,"
                             "updated_at=:updated_at",
            ReturnValues="ALL_NEW"
        )
        response = {
            "statusCode": 201,
            "body": result['Attributes']
        }
        return response

    def add_access_token(self, oauth_payload,):
        """add new access token in AUTH DB"""
        payload = {}
        payload['access_token'] = oauth_payload['access_token']
        payload['access_token_expiry_time'] = oauth_payload['expires_in']
        payload['refresh_token'] = oauth_payload['refresh_token']
        payload['refresh_token_expiry_time'] = '604800'
        payload['token_type'] = oauth_payload['token_type']
        oauth_dbsvc = OAuth2AuthenticatorDBService(str(uuid.uuid1()))
        res = oauth_dbsvc.add_oauth2(payload)
        if res['statusCode'] == 201:
            logger.info(f"Successfully added access token in DB")
        return res

    def update_access_token(self, auth_config, refresh_token):
        """Get new access token by using refresh token and save it to DB"""

        oauth_svc = OAuth2AuthenticatorService(auth_config['authorize_url'], auth_config['callback_uri'], auth_config['client_id'],
                                               auth_config['client_secret'], auth_config['token_url'], auth_config['refresh_token_url'],
                                               auth_config['response_type'], auth_config['scope'], auth_config['state'])
        access_tokens_res = oauth_svc.get_new_access_token(refresh_token)
        if access_tokens_res['statusCode'] == 200:
            oath2_payload = {}
            oath2_payload['access_token'] = access_tokens_res['tokens']['access_token']
            oath2_payload['access_token_expiry_time'] = access_tokens_res['tokens']['expires_in']
            oath2_payload['refresh_token_expiry_time'] = '604800'
            oath2_payload['token_type'] = access_tokens_res['tokens']['token_type']
            oauth_dbsvc = OAuth2AuthenticatorDBService(self.__id)
            res = oauth_dbsvc.update_oauth2(oath2_payload)
            if res['statusCode'] == 201:
                logger.info(f"Successfully updated access token in DB {res}")
                return res
        else:
            logger.info(
            f"Failed to get access tokens from netsuite {access_tokens_res}")
        return access_tokens_res
