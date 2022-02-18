import json
import os
import datetime

import boto3
from boto3.dynamodb.conditions import Attr
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import parse
from flow.flow import FlowExecutionModel
from flow.constant import FLOW_SUCCESS, FLOW_FAILURE
from common.response_code import ResponseClass
from common.constant import DATE_FORMAT

logger = Logger(service="flow")


""" Class for handling operations on flow execution."""

def parser_function(payload):
    try:
        return parse(model=FlowExecutionModel, event=payload)
    except Exception as err:
        logger.exception(err)
        raise KeyError from err

class FlowExecutionService:
    def __init__(self, flow_id, corelation_id, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.flow_id = flow_id
        self.corelation_id = corelation_id
        self.__current_timestamp = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        self.__table = dynamodb.Table(os.environ['FLOW_EXECUTION_TABLE'])
    
    def get_flow_executions_by_id(self, headers):
        """ Method for fetching the Flow object using it's id. """
        logger.info(f"Getting Exceution list for flow"
                    f"{self.flow_id}")
        result = self.__table.scan(
            FilterExpression=Attr("flow_id").eq(self.flow_id))
        if result["Count"] > 0:
            ok_response = {
                "statusCode": 200,
                "body": json.dumps(result['Items']),
                "headers": headers
            }
            logger.info(f"Flow Executions found with this id {self.flow_id}")
            return ok_response
        logger.info(f"No Flow Executions found with this id {self.flow_id}")
        responses = ResponseClass(headers)
        return responses.not_found_response()
    
    def create_flow_execution(self, execution_payload):
        """ Method for creating Flow Execution. """
        logger.info(f"Creating Flow Exceution entry in db for execution "
                    f"{self.corelation_id}")
        execution_payload['created_at'] = self.__current_timestamp
        execution_payload['updated_at'] = self.__current_timestamp
        parser_function(execution_payload)
        self.__table.put_item(Item=execution_payload)
        logger.info(f"Created Flow Exceution entry in db for execution "
                    f"{self.corelation_id} with {execution_payload} ")
        return execution_payload
    
    def update_flow_execution(self, flow_execution_payload):
        """ Method for updating Flow """
        logger.info(f"Update payload is {flow_execution_payload}")
        result = self.__table.update_item(
            Key={
                # 'flow_id': self.flow_id,
                'execution_id': self.corelation_id
            },
            ExpressionAttributeNames={
                "#status": "status",
            },
            ExpressionAttributeValues={
                ":status": flow_execution_payload.get("status"),
                ":updated_at": self.__current_timestamp
            },
            UpdateExpression="set #status=:status,"
            "updated_at=:updated_at",
            ReturnValues="ALL_NEW"
        )
        logger.info(f"Response from update item {result}")
        return result


    def update_execution_status(self, adapter_action_response, flow_obj):
        logger.info(f"Updating status for Exceution"
                    f"{self.corelation_id}")
        if adapter_action_response['statusCode'] == 201:
            logger.info(f" {self.corelation_id} Execution is successful")
            flow_obj['status'] = FLOW_SUCCESS
        else:
            logger.info(f" {self.corelation_id} Execution is failed")
            flow_obj['status'] = FLOW_FAILURE
        
        self.update_flow_execution(flow_obj)
            
        
    def get_execution_by_status(self, headers, status):
        logger.info(f"Getting {status} Exceutions for"
                    f"{self.flow_id}")
        result = self.__table.scan(
            FilterExpression=Attr("status").eq(status)
            & Attr("flow_id").eq(self.flow_id))
        if result["Count"] > 0:
            ok_response = {
                "statusCode": 200,
                "body": json.dumps(result['Items']),
                "headers": headers
            }
            logger.info(f"Flow Executions found with this id {self.flow_id} and status {status}")
            return ok_response
        logger.info(f"No Flow Executions found with this id  {self.flow_id} and status {status}")
        responses = ResponseClass(headers)
        return responses.not_found_response()
