import json
import uuid
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools import Logger
from common.cors import cors_headers
from filter.filter import Filter
from filter.filter_service import FilterService

from common.response_code import ResponseClass
from common.utils import check_if_not_none, check_if_empty, check_if_none


logger = Logger(service="filter")


def parser_function(payload):
    try:
        return parse(model=Filter, event=payload)
    except Exception as err:
        logger.exception(err)
        raise KeyError from err

# Create
@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def create(event, context):
    headers = cors_headers(event)
    try:
        logger.info(f'The context in this event is {context}')
        logger.info(f'This is the event {event}')
        # data = json.loads(event)
        # body= data["body"]
        payload_body= json.loads(event.get("body"))
        logger.info(f"Event's body {payload_body}")
        if 'id' in payload_body.keys():
            check_if_not_none("id", payload_body["id"])

        filter_service = FilterService(str(uuid.uuid1()))
        # payload_body= data["body"]
        logger.info(f"event's body {payload_body}")
        parser_function(payload_body)
        # event_str = json.dumps(payload_body)
        # item = json.loads(event_str)
        filter= filter_service.create_filter(payload_body)

        # create a response
        response = {
            "statusCode": 201,
            "body": json.dumps(filter),
            "headers": headers
        }
        logger.info(f"filter create restapi response {response}")
        return response
    except KeyError as err:
        logger.info("error captures is %s", err)
        raise KeyError from err

# Get

@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get(event, context):
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    try:
        logger.info(f'The context in this event is {context}')

        check_if_none("id", event['pathParameters']['id'])
        check_if_empty("id", event['pathParameters']['id'])

        filter_service = FilterService(event['pathParameters']['id'])
        result = filter_service.get_filter_by_id()
        logger.info(f"get filter restapi result {result}")
        if result and 'Item' in result:
            response = {
                "statusCode": 201,
                "body": json.dumps(result['Item']),
                "headers": headers
            }
            return response
        logger.info("No Filter found with this id %s", event['pathParameters']['id'])
        return responses.not_found_response()
    except KeyError:
        logger.info("No Filter found with this id %s", event['pathParameters']['id'])
        return responses.not_found_response()


# Update

def update(event, context):
    headers = cors_headers(event)
    try:
        logger.info(f'The context in this event is {context}')
        logger.info(
            f"Filter id inside pathParameters value {event['pathParameters']['id']}")
        payload_body =  json.loads(event.get("body"))
        check_if_none("id", event['pathParameters']['id'])
        check_if_empty("id", event['pathParameters']['id'])
        filter_service = FilterService(event['pathParameters']['id'])
        parser_function(payload_body)
        result = filter_service.update_filter(payload_body, event['pathParameters']['id'])

        response = {
            "statusCode": 201,
            "body": json.dumps(result['Attributes']),
            "headers": headers
        }
        return response
    except KeyError as err:
        raise KeyError from err
