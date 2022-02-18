import json
import uuid


from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools import Logger
from authentication.OAuth2_authenticator_db_service import OAuth2AuthenticatorDBService

from adapter.adapter import Adapter
from adapter.adapter_service import AdapterService
from adapter.adapter_oauth2_service import AdapterOAuth2AuthenticatorService
from common.decimalencoder import DecimalEncoder
from common.utils import check_if_empty, check_if_none
from common.response_code import ResponseClass
from common.cors import cors_headers

logger = Logger(service="docuphase-ig-adapter")


def parser_function(payload):
    try:
        return parse(model=Adapter, event=payload)
    except Exception as err:
        logger.exception(err)
        raise KeyError from err

# Create


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def create(event, context):
    """Method to expose a REST API to create Adapter"""
    logger.info(f"The context in this event is {context}")
    headers = cors_headers(event)
    # data = json.loads(event)
    # body= data["body"]
    # payload_body= json.loads(body)
    # payload_body= data["body"]
    payload_body = json.loads(event.get("body"))
    logger.info(f"The context in this event is {event}")
    adapter_service = AdapterService(str(uuid.uuid1()))
    # event_str = json.dumps(payload_body)
    # item = json.loads(event_str)
    parser_function(payload_body)
    adapter = adapter_service.create_adapter(payload_body)
    # create a response
    response = {
        "statusCode": 201,
        "body": json.dumps(adapter),
        "headers": headers
    }
    logger.info(f"Adapter create restapi response {response}")
    return response

# Get


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get(event, context):
    """Method to expose a REST API to get Adapter"""
    headers = cors_headers(event)
    try:
        logger.info(f"The context in this event is {context}")

        check_if_none('id', event['pathParameters']['id'])
        check_if_empty('id', event['pathParameters']['id'])
        adapter_service = AdapterService(event['pathParameters']['id'])

        result = adapter_service.get_adapter_by_id()
        logger.info(f'get response at restapi{result}')
        if result and 'Item' in result:
            parse(event=result['Item'], model=Adapter)

            response = {
                "statusCode": 201,
                "body": json.dumps(result['Item']),
                "headers": headers
            }
            logger.info(f"Successfully found Adapter response is {response}")
            return response
        responses = ResponseClass(headers)
        logger.info(
            f"No Adapter found with this id {event['pathParameters']['id']}")
        return responses.not_found_response()
    except KeyError:
        responses = ResponseClass(headers)
        logger.info(
            f"No Adapter found with this id {event['pathParameters']['id']}")
        return responses.not_found_response()


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get_list(event, context):
    """Method to expose a REST API to get list of all adapter"""
    logger.info(f"The context in this event is {context}")
    headers = cors_headers(event)
    adapter_service = AdapterService(str(uuid.uuid1()))
    result = adapter_service.get_adapter_list()

    data = result['Items']

    if data:
        for item in data:
            parse(event=item, model=Adapter)

    response = {
        "statusCode": 201,
        "body": json.dumps(data, cls=DecimalEncoder),
        'headers': headers
    }

    return response

# REST API FOR ADAPTER OAUTH2 AUTHENTICATION


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get_access_token_using_auth_code(event, context):
    """ Method to expose a REST API to get the access token for adapter """
    logger.info(f"The context in this event is {context}")
    oauth_obj = AdapterOAuth2AuthenticatorService(
        event['pathParameters']['id'])
    auth_code = (json.loads(event.get("body")))['auth_code']
    access_tokens_res = oauth_obj.get_access_token(auth_code)
    if access_tokens_res['statusCode'] == 200:
        oauth2db_obj = OAuth2AuthenticatorDBService(str(uuid.uuid1()))
        response = oauth2db_obj.add_access_token(access_tokens_res['tokens'])
        return response
    logger.info("Failed to get access token for Netsuite")
    return access_tokens_res


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get_authorization_auth_url(event, context):
    """ Method to expose a REST API to get the authorization url adapter auth"""
    logger.info(f"The context in this event is {context}")
    oauth_obj = AdapterOAuth2AuthenticatorService(
        event['pathParameters']['id'])
    url_res = oauth_obj.get_authorization_url()
    return url_res


# @logger.inject_lambda_context
# @logger.inject_lambda_context(log_event=True)
# def get_adapter_action_list(event, context):
#     """ Method to expose a REST API to get the adapter action list"""
#     logger.info(f"The context in this event is {context}")
#     adapter_service = AdapterService(event['pathParameters']['id'])
#     action_list = adapter_service.get_adapter_action_details_by_id()
#     return action_list
