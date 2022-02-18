""" This package implements Oauth configuration information service layer. """
import json
import uuid

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from common.cors import cors_headers
from common.response_code import ResponseClass

from adapter.adapter import AdapterOauth
from adapter.adapter_oauth_config_service import AdapterOAuthConfigService

logger = Logger(service="docuphase-ig-auth-info")


def parser_function(payload):
    try:
        return parse(model=AdapterOauth, event=payload)
    except Exception as err:
        logger.exception(err)
        raise KeyError from err


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def create(event, context=LambdaContext):
    """Method to expose a REST API to create Adapter config"""
    logger.info(f"The context in this event is {context}")
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    body = json.loads(event.get("body"))
    parser_function(body)
    auth_id = str(uuid.uuid1())
    body["id"] = auth_id
    oauth_obj = AdapterOAuthConfigService(auth_id)
    result = oauth_obj.create_oauth_config(body)
    logger.info(f"reult from create {result}")
    if result['ResponseMetadata']['HTTPStatusCode'] == 200:
        ok_response = {
            "statusCode": 200,
            "body": json.dumps(body),
            "headers": headers
        }
        logger.info("Entry created {ok_response}")
        return ok_response
    logger.info(
        f"The config entry couldn't be created {responses.not_implimented_error()}")
    return responses.not_implimented_error()

def get(event, context=LambdaContext):
    """Method to expose a REST API to create Adapter config"""
    logger.info(f"The context in this event is {context}")
    headers = cors_headers(event)
    auth_id = event["pathParameters"]["id"]
    responses = ResponseClass(headers)
    oauth_obj = AdapterOAuthConfigService(auth_id)
    result = oauth_obj.get_oauth_config_by_id()
    logger.info(f"reult from create {result}")
    if result['statusCode'] == 201:
        ok_response = {
            "statusCode": 201,
            "body": json.dumps(result['body']),
            "headers": headers
        }
        logger.info("Entry created {ok_response}")
        return ok_response
    logger.info(
        f"The config entry couldn't be created {responses.not_found_response()}")
    return responses.not_found_response()
