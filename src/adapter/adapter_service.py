import os
import datetime
import json
import boto3

from aws_lambda_powertools import Logger
from authentication.OAuth2_authenticator_db_service import OAuth2AuthenticatorDBService
from adapter.adapter_factory import AdapterFactory


from adapter.adapter_oauth_config_service import AdapterOAuthConfigService
from common.response_code import ResponseClass
from common.constant import DATE_FORMAT
logger = Logger(service="docuphase-ig-adapter")


class AdapterService:
    def __init__(self, adapter_id, function_name=None, corelation_id=None, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource(
                'dynamodb', region_name=os.environ['AWS_REGION'])
        self.__id = adapter_id
        self.__function_name = function_name
        self.__corelation_id = corelation_id
        self.__current_timestamp = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        self.__table = dynamodb.Table(os.environ['ADAPTER_TABLE'])

    def get_adapter_action_details_by_id(self):
        """ Return adapter actions details """
        result = self.get_adapter_by_id()
        logger.info(f'get response at service{result}')
        return result

    def get_all_adapter_list(self):
        """Return all available Adapter list """
        result = self.get_adapter_list()
        if len(result['Items']) > 0:
            logger.info("Adapter List is found")
            return result
        logger.info("No Adapter List is found")
        return None

    def get_adapter_type_by_id(self):
        """Return Adapter Type"""
        result = self.get_adapter_by_id()
        if result and 'Item' in result.keys():
            item = result['Item']
            logger.info(f"The adapter result from get call {item}")
            return item['type']
        logger.info(f"No Adapter found with this id {self.__id}")
        return None

    def get_adapter_object_and_call_adapter_action(self, adapter_type, data,
                                                   auth_id, auth_config_id):
        """Get Adapter Object and Perform ERP specific Action"""
        logger.info(
            f"corelation id at apply adapter with Execution Id {self.__corelation_id}")
        adapter_object = AdapterFactory.get_adapter_object(
            adapter_type, self.__corelation_id)
        if adapter_object is not None:
            logger.info(f"The Returned Adapter Object created {adapter_object}"
                        f"as per given adapter type {adapter_type}")
            logger.info(f"Getting access token from Authenticator"
                        f"table with Execution Id {self.__corelation_id}")
            oauth_obj = OAuth2AuthenticatorDBService(auth_id)
            token_response = oauth_obj.get_oauth2_by_id()
            if token_response['statusCode'] == 201:
                valid = self.check_for_access_token_valid(token_response)
                if valid:
                    response = self.perform_action(adapter_object,
                                                   token_response['Item']['access_token'], data)
                    return response
                res = self.update_invalid_token(auth_id, token_response,
                                                auth_config_id)
                if res['statusCode'] == 201:
                    response = self.perform_action(adapter_object,
                                                   res['body']['access_token'], data)
                    return response
                return res
            return token_response
        return None

    def check_for_access_token_valid(self, token_response):
        """This method will check if access token is valid or not"""
        logger.info(f"Token response form Authenticator {token_response}")
        logger.info(
            f"Checking access token valid time with Execution Id  {self.__corelation_id}")
        updated_datetime = datetime.datetime.strptime(
            token_response['Item']['updated_at'], '%Y-%m-%d %H:%M:%S.%f')
        logger.info(f"Updated Time of access token from DB  {updated_datetime}"
                    f"with Execution Id  {self.__corelation_id}")
        expires_in_obj = updated_datetime + datetime.timedelta(
            seconds=int(token_response['Item']['access_token_expiry_time']))
        logger.info(f"Token will be expired at  {expires_in_obj}"
                    f"with Execution Id  {self.__corelation_id}")
        if expires_in_obj > datetime.datetime.utcnow():
            logger.info(
                f"Access Token is valid with Execution Id  {self.__corelation_id}")
            return True
        logger.info(
            f"Access Token is not valid with Execution Id {self.__corelation_id}")
        return False

    def update_invalid_token(self, auth_id, token_response,
                             auth_config_id):
        """Method to update access token in auth DB"""
        oauth_obj = OAuth2AuthenticatorDBService(auth_id)
        logger.info("Access Token is expired ,requesting new access token"
                    f"with Excecution Id {self.__corelation_id}")
        adapter_auth_svc = AdapterOAuthConfigService(auth_config_id)
        auth_config = adapter_auth_svc.get_oauth_config_by_id()
        if auth_config['statusCode'] == 201:
            res = oauth_obj.update_access_token(auth_config['body'],
                                                token_response['Item']['refresh_token'])
            if res['statusCode'] == 201:
                logger.info("Token updated successfully, performing action with new access token "
                            f"with Excecution Id {self.__corelation_id}")
                return res
            logger.info(f"Unable to update Access token {res} with"
                        f"Excecution Id {self.__corelation_id}")
            return res
        return auth_config

    def perform_action(self, adapter_object, access_token, data):
        do_action = f"do_{self.__function_name}"
        logger.info(f"Performing this actions ----->"
                    f"{do_action} with Execution Id {self.__corelation_id}")
        if hasattr(adapter_object, do_action) and callable(func :=
                                                           getattr(adapter_object, do_action)):
            response = func(data,
                            access_token)
            logger.info(f"Response got from perform action {response}"
                        f"with Excecution Id {self.__corelation_id}")
            return response
        responses = ResponseClass("headers")
        return responses.not_found_response()

    def get_adapter_by_id(self):
        """ Method for fetching the Adapter object using it's id. """
        result = self.__table.get_item(
            Key={
                'id': self.__id
            }
        )
        if 'Item' in result.keys():
            return result
        logger.info(f"No Adapter found with this id {self.__id}"
                    f"with Excecution Id {self.__corelation_id}")
        return None

    def get_adapter_list(self):
        """Return Adapter List"""
        result = self.__table.scan()
        return result

    def create_adapter(self, adapter_payload):
        """ Method for creating Adapter. """
        # adapter_payload= json.loads(adapter_payload)
        adapter_payload['id'] = self.__id
        adapter_payload['created_at'] = self.__current_timestamp
        adapter_payload['updated_at'] = self.__current_timestamp
        payload_str = json.dumps(adapter_payload)
        adapter = json.loads(payload_str)
        self.__table.put_item(Item=adapter)
        return adapter
