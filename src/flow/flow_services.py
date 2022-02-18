import json
import os
import datetime

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.conditions import Attr
from common.response_code import ResponseClass
from common.constant import DATE_FORMAT

logger = Logger(service="flow")


""" Class for handling operations on flow."""


class FlowService:

    def __init__(self, flow_id, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.flow_id = flow_id
        self.__current_timestamp = datetime.datetime.utcnow().strftime(DATE_FORMAT)
        self.__table = dynamodb.Table(os.environ['FLOW_TABLE'])

    def get_flow_by_id(self, headers):
        """ Method for fetching the Flow object using it's id. """
        result = self.__table.get_item(
            Key={
                'flow_id': self.flow_id
            }
        )
        if 'Item' in result.keys():
            ok_response = {
                "statusCode": 200,
                "body": json.dumps(result['Item']),
                "headers": headers
            }
            logger.info(f"Flow found with this id {self.flow_id}")
            return ok_response
        logger.info(f"No Flow found with this id {self.flow_id}")
        responses = ResponseClass(headers)
        return responses.not_found_response()

    def update_flow(self, flow_payload, flow_key):
        """ Method for updating Flow """
        logger.info(f"input is {flow_payload}")
        result = self.__table.update_item(
            Key={
                'flow_id': flow_key
            },
            ExpressionAttributeNames={
                "#status": "status",
                "#name": "name",
                "#desc": "desc",
                "#flowstep": "flowstep",
                "#auth_id": "auth_id",
                "#flow_url": "flow_url"
            },
            ExpressionAttributeValues={
                ":name": flow_payload.get("name"),
                ":desc": flow_payload.get("desc"),
                ":status": flow_payload.get("status"),
                ":flowstep": flow_payload.get("flowstep"),
                ":auth_id": flow_payload.get("auth_id"),
                ":flow_url": flow_payload.get("flow_url"),
                ":updatedAt": self.__current_timestamp
            },
            UpdateExpression="set #name=:name, #desc=:desc,"
            "#status=:status, #flowstep=:flowstep,"
            "#flow_url=:flow_url,"
            "#auth_id=:auth_id, updatedAt=:updatedAt",
            ReturnValues="ALL_NEW"
        )
        logger.info(f"Response from update item {result}")
        return result

    def create_flow(self, flow_payload, headers):
        """ Method for creating Flow. """
        flow_payload['flow_id'] = self.flow_id
        flow_payload['flow_url'] = flow_payload.get("name") + '/' + flow_payload['flow_id']
        flow_payload['created_at'] = self.__current_timestamp
        flow_payload['updated_at'] = self.__current_timestamp
        check_if_name_exists = self.__table.scan(
            FilterExpression=Attr("name").eq(flow_payload.get("name")))
        logger.info(
            f"Checking if any flow with the same name exists {check_if_name_exists}")
        if check_if_name_exists["Count"] == 0:
            self.__table.put_item(Item=flow_payload)
            return flow_payload
        already_exists_error = {
            "statusCode": 403,
            "body": json.dumps("Please assign the flow another name"),
            "headers": headers
        }
        return already_exists_error

    def get_flow_list(self, limit=0, exclusive_start_key=None):
        if exclusive_start_key is not None:
            result = self.__table.scan(
                Limit=limit, ExclusiveStartKey=exclusive_start_key)
        else:
            result = self.__table.scan(
                Limit=limit)
        return result
