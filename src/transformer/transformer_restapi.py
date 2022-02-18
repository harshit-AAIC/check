""" This package impements REST API's for transformer. """
import uuid
import json

from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools import Logger
from common.cors import cors_headers

from transformer.transformer import Transformer
from transformer.transformer_service import TransformerService

from common.response_code import ResponseClass
from common.utils import check_if_none, check_if_not_none, check_if_empty


logger = Logger(service="docuphase-ig-transformer")

def parser_function(payload):
    try:
        return parse(model=Transformer, event=payload)
    except Exception as err:
        logger.exception(err)
        raise KeyError from err

# Create

@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def create(event, context):
    """ Method to expose create transformer REST API. """
    headers = cors_headers(event)
    try:
        logger.info("The context in this event is %s", context)
        payload_body = json.loads(event.get("body"))
        logger.info(f"Event's body {payload_body}")
        if "id" in payload_body.keys():
            check_if_not_none("id", payload_body["id"])
        transformer_service = TransformerService(str(uuid.uuid1()))
        parser_function(payload_body)
        transformer = transformer_service.create_transformer(payload_body)
        # create a response
        response = {
            "statusCode": 201,
            "body": json.dumps(transformer),
            "headers": headers
        }
        logger.info(f"Successfully Created item {response}")
        return response
    except KeyError as err:
        raise KeyError from err


# Get

@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get(event, context):
    """ Method to expose get transformer REST API. """
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    try:
        logger.info("The context in this event is %s", context)
        check_if_none('id', event['pathParameters']['id'])
        check_if_empty('id', event['pathParameters']['id'])
        logger.info("The event is %s", event)
        transformer_service = TransformerService(event['pathParameters']['id'])
        result = transformer_service.get_transformer_by_id()

        if result and 'Item' in result:
            response = {
                "statusCode": 201,
                "body": json.dumps(result['Item']),
                "headers": headers
            }
            logger.info(f"Successfully found item {response}")
            return response

        return responses.not_found_response()
    except KeyError:
        return responses.not_found_response()

# Update

@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def update(event, context):
    """ Method to expose update transformer REST API. """
    headers = cors_headers(event)
    try:
        logger.info(f"The context in this event is {context} ")
        logger.info(
            f"Transformer id inside pathParameters value {event['pathParameters']['id']}")
        payload_body = json.loads(event.get("body"))
        check_if_none("id", event['pathParameters']['id'])
        check_if_empty("id", event['pathParameters']['id'])
        transformer_service = TransformerService(event['pathParameters']['id'])
        parser_function(payload_body)
        result = transformer_service.update_transformer(payload_body, event['pathParameters']['id'])
        logger.info(f"The Update result  is {result}")
        response = {
            "statusCode": 201,
            "body": json.dumps(result['Attributes']),
            "headers": headers
            }
        logger.info(f"Successfully updated item {response}")
        return response
    except KeyError as err:
        raise KeyError from err

def transform(event, context):
    """ Method to expose a REST API for transform feature of the transformer. """
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    try:
        logger.info("The context in this event is %s", context)
        transformed_object = TransformerService.transform(event['mapping'], event['input_payload'])
        if transformed_object:
            response = {
                "statusCode": 200,
                "body": json.dumps(transformed_object),
                "headers": headers
            }
            return response
        return responses.not_found_response()

    except KeyError:
        return responses.bad_request()
    except ValueError:
        return responses.bad_request()
