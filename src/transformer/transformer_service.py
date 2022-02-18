""" This package impements a service for transformer. """
from datetime import datetime
import os
import json
import jq
import boto3
from aws_lambda_powertools import Logger

logger = Logger(service="docuphase-ig-transformer")

""" Class for handling operations on transformer. """
class TransformerService:

    def __init__(self, transformer_id, dynamodb = None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
        self.__id = transformer_id
        self.__current_timestamp = str(datetime.utcnow().timestamp())
        self.__table = dynamodb.Table(os.environ['TRANSFORMER_TABLE'])

    def __get_mapping_by_id(self):
        """ Private method to fetch the mapping object using the transformer Id. """
        result = self.get_transformer_by_id()
        if result and 'Item' in result.keys():
            item = result['Item']
            logger.info("The transformer result from get call %s", item)
            return item['mapping_payload']
        logger.info("No Transformer found with this id %s", self.__id)
        return None

    @classmethod
    def transform(cls, mapping, payload_to_transform):
        """ Core class method for converting input data based on mapping. """
        logger.info(f"Mapping definition received {mapping}")
        logger.info(f"Input payload received {payload_to_transform}")
        mapping_string = json.dumps(mapping).replace('"','')
        return jq.all(mapping_string, payload_to_transform)[0]

    def create_transformer(self, transformer_payload):
        """ Method for creating transformer. """
        transformer_payload['id'] = self.__id
        transformer_payload['created_at'] = self.__current_timestamp
        transformer_payload['updated_at'] = self.__current_timestamp
        payload_str = json.dumps(transformer_payload)
        transformer = json.loads(payload_str)
        self.__table.put_item(Item=transformer)
        return transformer

    def get_transformer_by_id(self):
        """ Method for fetching the transformer object using it's id. """
        result = self.__table.get_item(
                Key={
                    'id': self.__id
                }
            )
        if 'Item' in result.keys():
            return result
        logger.info(f"No Transformer found with this id {self.__id}")
        return None

    def update_transformer(self, transformer_payload, transformer_key):
        """ Method for updating transformer. """
        result = self.__table.update_item(
            Key={
                'id': transformer_key
            },
            ExpressionAttributeNames={
                "#status": "status",
                "#name": "name",
                "#input_payload": "input_payload",
                "#mapping_payload": "mapping_payload"
            },
            ExpressionAttributeValues={
                ":name": transformer_payload['name'],
                ":status": transformer_payload['status'],
                ":input_payload": transformer_payload['input_payload'],
                ":mapping_payload": transformer_payload['mapping_payload'],
                ":updated_at": self.__current_timestamp
            },
            UpdateExpression="set #name=:name,"
                             "#status=:status, #mapping_payload=:mapping_payload,"
                             "#input_payload=:input_payload,"
                             "updated_at=:updated_at",
            ReturnValues="ALL_NEW"
        )
        return result

    def transform_by_id(self, payload_to_transform,corelation_id):
        """ Method for converting input data based on the transformer id. """
        logger.info(f"Corelation id at apply transformer {corelation_id}")
        transformer_mapping = self.__get_mapping_by_id()
        if transformer_mapping is None:
            logger.info(f"Could not find mapping for the transformer with id "
                        f"{self.__id} with Excecution Id {corelation_id} ")
            return None
        return self.transform(transformer_mapping, payload_to_transform)
