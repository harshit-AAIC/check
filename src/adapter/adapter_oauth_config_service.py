""" This package implements Oauth configuration information service layer. """
import os

import boto3
from aws_lambda_powertools import Logger
from common.response_code import ResponseClass

""" Class for OAuth authentication info with different adapters. """
logger = Logger(service="docuphase-ig-auth-info")


class AdapterOAuthConfigService:
    """Class init """

    def __init__(self, oauth_id, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource(
                'dynamodb', region_name=os.environ['AWS_REGION'])
        self.__id = oauth_id
        self.__table = dynamodb.Table(
            os.environ['OAUTH_CONFIG_DYNAMODB_TABLE'])

    def get_oauth_config_by_id(self):
        """ Method for fetching the oauth config info using it's id. """
        result = self.__table.get_item(
            Key={
                'id': self.__id
            }
        )
        if result and 'Item' in result:
            response = {
                "statusCode": 201,
                "body": result['Item']
            }
            return response
        responses = ResponseClass("headers")
        logger.info(
            f"No oauth2 entry found with this id {self.__id} response {responses.not_found_response()}")
        return responses.not_found_response()

    def create_oauth_config(self, body):
        """ Method for creating a new entry in auth table. """
        result = self.__table.put_item(
            Item=body
        )
        return result
