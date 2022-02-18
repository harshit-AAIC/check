import base64
import json
import os
import uuid
import datetime
import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.typing.lambda_context import LambdaContext
from adapter.adapter_service import AdapterService
from filter.filter_restapi import FilterService
from flow.flow_execution_service import FlowExecutionService
from flow.flow_services import FlowService
from flow.flow import Flow
from flow.constant import FLOW_RUNNING
from transformer.transformer_service import TransformerService
from common.response_code import ResponseClass
from common.cors import cors_headers
from common.utils import check_if_none
from common.constant import DATE_FORMAT


def parser_function(payload):
    try:
        return parse(model=Flow, event=payload)
    except Exception as err:
        logger.exception(err)
        raise KeyError from err


# Create
logger = Logger(service="flow")

DYNAMODB = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
flow_table = DYNAMODB.Table(os.environ['FLOW_TABLE'])


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def create(event, context):
    logger.info(f"The context for this is {context}")
    headers = cors_headers(event)
    data = json.loads(event.get("body"))
    logger.info(f"event's body {data}")
    parser_function(data)
    flow_service = FlowService(str(uuid.uuid1()))
    create_data = flow_service.create_flow(data, headers)
    logger.info(f"The final data to be appended in the table {create_data}")
    if "statusCode" not in create_data:
        ok_response = {
            "statusCode": 201,
            "body": json.dumps(create_data),
            "headers": headers
        }
        logger.info(f"response for put_item {ok_response}")
        return ok_response
    return create_data

# List


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get_list(event, context):
    logger.info(f"The context for this is {context}")
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    flow_service = FlowService(None)
    if event['queryStringParameters']:
        pagination_token = event['queryStringParameters'].get(
            'pagination_token')
        limit = int(event['queryStringParameters'].get('limit', 20))
    else:
        pagination_token = None
        limit = 20

    if pagination_token is not None:
        try:
            pagination_token_bytes = pagination_token.encode("ascii")
            decoded_binary_secret = base64.b64decode(pagination_token_bytes)
            decoded_token = decoded_binary_secret.decode("ascii")
            exclusive_start_key = {'flow_id': decoded_token}
        except Exception as error:  # pylint: disable=broad-except
            logger.info("error while decoding token %s", error)
            return responses.bad_request()
        result = flow_service.get_flow_list(limit, exclusive_start_key)
    else:
        result = flow_service.get_flow_list(limit)

    data = result['Items']

    if 'LastEvaluatedKey' in result:
        lek = result['LastEvaluatedKey']['id']
        lek_bytes = lek.encode("ascii")
        pagination_token_bytes = base64.b64encode(lek_bytes)
        pagination_token = pagination_token_bytes.decode("ascii")
    else:
        pagination_token = ""

    response = {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(data)
    }

    return response


# get
@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get(event, context):
    headers = cors_headers(event)
    try:
        logger.info(f"The context for this is {context}")
        logger.info(f"The event is {event}")
        flow_id = check_if_none("id", event['pathParameters']['id'])
        logger.info(f"The table id {flow_id}")
        flow_service = FlowService(flow_id)
        result = flow_service.get_flow_by_id(headers)
        logger.info(f"response for get flow by id {result}")
        return result

    except KeyError as keyerror:
        raise KeyError from keyerror

# Update


@logger.inject_lambda_context
@logger.inject_lambda_context(correlation_id_path="headers.my_request_id_header")
@logger.inject_lambda_context(log_event=True)
def update(event, context):
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    try:
        logger.info(f"The context for this is {context}")
        logger.info(
            f"flow_id inside pathParameters value {event['pathParameters']['id']}")
        if event['pathParameters']['id'] is None:
            raise ValueError
        flow_id = event['pathParameters']['id']
        data = json.loads(event['body'])
        response = parser_function(data)
        logger.info(f"parser response {response}")
        flow_service = FlowService(flow_id)
        result = flow_service.update_flow(data, flow_id)
        ok_response = {
            "statusCode": 200,
            "body": json.dumps(result['Attributes']),
            "headers": headers
            }
        return ok_response
    except KeyError:
        return responses.not_found_response()


@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def process(event, context):
    logger.info(f"The context for this is {context}")
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    corelation_id = str(uuid.uuid1())
    corelation_id = corelation_id.replace("-","_")
    started_at = datetime.datetime.utcnow().strftime(DATE_FORMAT)
    flow_execution = FlowExecutionService(event['pathParameters']['id'], corelation_id)
    flow_execution_obj = {
                "flow_id": event['pathParameters']['id'],
                "execution_id": corelation_id,
                "status" : FLOW_RUNNING,
            }
    flow_execution.create_flow_execution(flow_execution_obj)
    logger.info(f"<-------- Execution started at -----> {started_at}")
    logger.info(f"Corelation id at flow process {corelation_id}")
    event_body = json.loads(event.get("body"))
    logger.info(f"Event body{event_body} with Excecution Id {corelation_id}")
    flow_json = get(event, context=LambdaContext)
    if flow_json['statusCode'] == 200:
        flow = json.loads(flow_json.get("body"))
        logger.info(f"Get response from get flow {flow_json} with Excecution Id {corelation_id}")
        filter_id = flow["flowstep"][0]["filter_id"]
        logger.info(f"Filter id {filter_id}")
        before_transformer_id = flow["flowstep"][0]["before_transformer_id"]
        logger.info(f"Before Transformer id {before_transformer_id} with Excecution Id {corelation_id}")
        adapter_id = flow["flowstep"][0]["adapter_id"]
        logger.info(f"Adapter id {adapter_id} with Excecution Id {corelation_id}")
        adapter_action_name = flow["flowstep"][0]["action_name"]
        logger.info(f"Adapter action name {adapter_action_name} with Excecution Id {corelation_id}")
        adapter_service = AdapterService(
            adapter_id, adapter_action_name, corelation_id)
        auth_id = flow['auth_id']
        transformer_service = TransformerService(before_transformer_id)
        filter_service = FilterService(filter_id)
        logger.info(
            f"Apply filter inputs and types {event_body} {type(event_body)} {corelation_id} {type(corelation_id)}")
        apply_filter_response = filter_service.apply_filter_result(
            event_body, corelation_id)
        logger.info(f"Apply filter response {apply_filter_response} with Excecution Id {corelation_id}")
        if apply_filter_response:
            mapped_data = transformer_service.transform_by_id(
                json.loads((event.get("body"))), corelation_id)
            logger.info(f"Mapping data after transformation {mapped_data}"
                        f" with Excecution Id {corelation_id}")
            adapter_obj = adapter_service.get_adapter_by_id()
            adapter_action_response = adapter_service.get_adapter_object_and_call_adapter_action(
                adapter_obj['Item']['type'], mapped_data,
                auth_id,
                adapter_obj['Item']['what_auth_id'])
            logger.info(f"Returned response from adapter-perform action"
                        f"{adapter_action_response} with Excecution Id {corelation_id}")
            logger.info(f"<-------- Execution completed at -----> {started_at}")
            flow_execution.update_execution_status(adapter_action_response, flow_execution_obj)
            return adapter_action_response
        return responses.filter_failed()
    return responses.not_found_response()


def get_sample_input_payload(event, context):
    logger.info(f"The context for this is {context} ")
    headers = cors_headers(event)
    responses = ResponseClass(headers)
    flow_json = get(event, context=LambdaContext)
    flow = json.loads(flow_json.get("body"))
    before_transformer_id = flow["flowstep"][0]["before_transformer_id"]
    transformer_service = TransformerService(before_transformer_id)
    transformer_object = transformer_service.get_transformer_by_id()
    if transformer_object is None:
        logger.info(
            f"Couldn't find transformer object for the transformer with id {before_transformer_id}")
        return responses.not_found_response( )
    
    transformer_input_payload = transformer_object['Item']['input_payload']
    response = {
        "statusCode": 201,
         "body": json.dumps(transformer_input_payload),
         "headers": headers
    }
    logger.info(f"input payload for transformer {transformer_input_payload}")
    return response

@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get_flow_execution_list(event, context):
    headers = cors_headers(event)
    try:
        logger.info(f"The context for this is {context}")
        logger.info(f"The event is {event}")
        flow_id = check_if_none("id", event['pathParameters']['id'])
        logger.info(f"The flow execution table id {flow_id}")
        flow_execution_service = FlowExecutionService(flow_id, None)
        result = flow_execution_service.get_flow_executions_by_id(headers)
        logger.info(f"Response for get flow execution list by id {result}")
        return result
    except KeyError as keyerror:
        raise KeyError from keyerror

@logger.inject_lambda_context
@logger.inject_lambda_context(log_event=True)
def get_execution_by_status(event, context):
    headers = cors_headers(event)
    try:
        logger.info(f"The context for this is {context}")
        logger.info(f"The event is {event}")
        flow_id = check_if_none("id", event['pathParameters']['id'])
        status = event['pathParameters']['status']
        flow_execution_service = FlowExecutionService(flow_id, None)
        result = flow_execution_service.get_execution_by_status(headers, status)
        logger.info(f"Response for {status} executions {result}")
        return result
    except KeyError as keyerror:
        raise KeyError from keyerror
