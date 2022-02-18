from datetime import datetime
import os
import json
import jq
import boto3
from aws_lambda_powertools import Logger
from filter.constants import constants

logger = Logger(service="docuphase-ig-filter")

def obj_dict(obj):
    return obj.__dict__


""" Class for handling operations on filter."""
class FilterService:

    def __init__(self, filter_id, dynamodb = None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.__id = filter_id
        self.__current_timestamp = str(datetime.utcnow().timestamp())
        self.__table = dynamodb.Table(os.environ['FILTER_TABLE'])

    def get_filter_by_id(self):
        """ Method for fetching the Filter object using it's id. """
        logger.info(f"filter id {self.__id}")
        result = self.__table.get_item(
                Key={
                    'id': self.__id
                }
            )
        return result

    def update_filter(self, filter_payload, filter_key):
        """ Method for updating Filter """
        json_filter_criteria = json.dumps(
            filter_payload["filter_criteria"], default=obj_dict)
        result = self.__table.update_item(
            Key={
                'id': filter_key
            },
            ExpressionAttributeNames={
                "#status": "status",
                "#name": "name",
            },
            ExpressionAttributeValues={
                ":name": filter_payload['name'],
                ":status": filter_payload['status'],
                ":filter_criteria": json.loads(json_filter_criteria),
                ":updated_at": self.__current_timestamp
            },
            UpdateExpression="set #name=:name,"
                             " #status=:status,filter_criteria=:filter_criteria," 
                             "updated_at=:updated_at",
            ReturnValues="ALL_NEW"
        )
        return result

    def create_filter(self, filter_payload):
        """ Method for creating Filter. """
        logger.info(f"filter create service input {filter_payload} and type {type(filter_payload)}")
        # filter_payload= json.loads(filter_payload)
        filter_payload['id'] = self.__id
        filter_payload['created_at'] = self.__current_timestamp
        filter_payload['updated_at'] = self.__current_timestamp
        # payload_str = json.dumps(filter_payload)
        # filter = json.loads(payload_str)
        logger.info(f"final input for table{filter_payload}")
        logger.info(f"final input for table{type(filter_payload)}")
        self.__table.put_item(Item=filter_payload)
        # logger.info(f"filter create service response {response}")
        return filter_payload

    def get_filter_criteria(self):
        result= self.get_filter_by_id()
        if 'Item' in result.keys():
            item = result['Item']
            logger.info(f"The filter result from get call {item}")
            if 'filter_criteria' in item.keys():
                filter_criteria = item['filter_criteria']
                logger.info(f"The filter result from get call {filter_criteria}")
                return filter_criteria

        logger.info(f"No Filter found with this id {self.__id}")
        return None

    @classmethod
    def apply_filter(cls, criteria, payload):
        jq_var= ""
        for obj in criteria:
            if obj["condition"] == constants["EQUAL_TO"]:
                value_1 = (f'"{obj["value"]}"')
                jq_var= jq_var+ "'." + \
                    str(obj["key"]) + " ==" + " " + value_1 + \
                    "' " + str(obj["operator"]) + " "
            elif obj["condition"] == constants["CONTAINS"]:
                if obj["key"] in payload:
                    value_2 = f'| test("(?i){obj["value"]}")'
                    jq_var= jq_var+ "'." + str(obj["key"]) + " " + \
                        value_2 + "' " + str(obj["operator"]) + " "
                else:
                    return False
            elif obj["condition"] == constants["HAS_KEY"]:
                value_3 = f'has("{obj["key"]}")'
                jq_var= jq_var+ "'" + value_3 + "' " + str(obj["operator"]) + " "
            elif obj["condition"] == constants["DOES_NOT_CONTAIN"]:
                if obj["key"] in payload:
                    value_4 = f'| test("(?i){obj["value"]}") | not)'
                    jq_var= jq_var+ "'(." + str(obj["key"]) + " " + \
                        value_4 + "' " + str(obj["operator"]) + " "
                else:
                    return False
            elif obj["condition"] == constants["NOT_EQUAL_TO"]:
                value_5 = f'== "{obj["value"]}" | not'
                jq_var= jq_var+ "'." + str(obj["key"]) + " " + \
                    value_5 + "' " + str(obj["operator"]) + " "
            elif obj["condition"] == constants["STARTSWITH"]:
                value_6 = f'| startswith("{obj["value"]}")'
                jq_var= jq_var+ "'." + str(obj["key"]) + " " + \
                    value_6 + "' " + str(obj["operator"]) + " "
            elif obj["condition"] == constants["ENDSWITH"]:
                value_7 = f'| endswith("{obj["value"]}")'
                jq_var= jq_var+ "'." + str(obj["key"]) + " " + \
                    value_7 + "' " + str(obj["operator"]) + " "
            elif obj["condition"] == constants["GREATER_THAN"]:
                value_8 = f'{obj["value"]}'
                jq_var= jq_var+ "'." + str(obj["key"]) + "> " + \
                    value_8 + "' " + str(obj["operator"]) + " "
            elif obj["condition"] == constants["LESS_THAN"]:
                value_9 = f'{obj["value"]}'
                jq_var= jq_var+ "'." + str(obj["key"]) + "< " + \
                    value_9 + "' " + str(obj["operator"]) + " "
        filter_result = jq.all(eval(jq_var), payload)[0]
        return filter_result

    def apply_filter_result(self, payload, corelation_id):
        logger.info(f"Corelation id at apply filter {corelation_id}")
        filter_criteria = self.get_filter_criteria()
        if filter_criteria is None:
            logger.info(f"Could not find filter criteria for the filter with id"
                        f"{self.__id} with Excecution Id {corelation_id}")
            return None
        return self.apply_filter(filter_criteria, payload)
