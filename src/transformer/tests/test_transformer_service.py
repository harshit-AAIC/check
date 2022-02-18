import os
import unittest
from moto import mock_dynamodb2
import boto3

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import  ValidationError
from aws_lambda_powertools import Logger

from transformer.transformer_service import TransformerService

logger = Logger(service="docuphase-ig-transformer")

sample_input_payload = {
  "name": "myVendor",
  "properties": {
    "billAddressList": {
      "internalId": "168362"
    }
  },
  "account": {
    "internalId": 233233
  },
  "currency": [
    "INR",
    "USD"
  ]
}

sample_mapping = {
    "vendor_name": ".name",
    "fields": ".properties",
    "accountInfo": ".account"
}

transformer_sample_object = {
    "id": "sdjmrsknlsfdgf",
    "name": "Oracle Transformer",
    "status": "Created",
    "input_payload": sample_input_payload,
    "mapping_payload": sample_mapping
}

@mock_dynamodb2
class TransformerServiceTest(unittest.TestCase):

    def setUp(self):
      """
      Create database resource and mock table
      """
      os.environ['AWS_REGION'] = "us-east-1"
      os.environ['TRANSFORMER_TABLE'] = "transformer-table"  
      self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
      self.table = self.dynamodb.create_table(
          TableName=os.environ['TRANSFORMER_TABLE'],
          KeySchema=[
              {
                  'AttributeName': 'id',
                  'KeyType': 'HASH'
              }
          ],
          AttributeDefinitions=[
              {
                  'AttributeName': 'id',
                  'AttributeType': 'S'
              }
          ],
          ProvisionedThroughput={
              'ReadCapacityUnits': 1,
              'WriteCapacityUnits': 1
          }
      )

    def tearDown(self):
      """
      Delete database resource and mock table
      """
      self.table.delete()
      self.dynamodb=None

    def test_transform(self):
      transformed_object = TransformerService.transform(sample_mapping, sample_input_payload)
      assert transformed_object['vendor_name'] == sample_input_payload['name']
    
    def test_transform_by_id(self):
      self.table.put_item(Item=transformer_sample_object)
      transformer_service = TransformerService(transformer_sample_object['id'], self.dynamodb)
      transformed_object = transformer_service.transform_by_id(sample_input_payload,"83e71c16-4912-11ec-a1a5-9a22ed39fc71")
      assert transformed_object['vendor_name'] == sample_input_payload['name']

    def test_transform_by_id_not_available(self):
      transformer_service = TransformerService(transformer_sample_object['id'], self.dynamodb)
      transformed_object = transformer_service.transform_by_id(sample_input_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
      assert transformed_object == None

    def test_create_transformer(self):
      transformer_service = TransformerService(transformer_sample_object['id'], self.dynamodb)
      create_transformer_response = transformer_service.create_transformer(transformer_sample_object)
      assert create_transformer_response['name'] == "Oracle Transformer"
    
    def test_update_transformer(self):
      self.table.put_item(Item=transformer_sample_object)
      transformer_sample_object['name'] = "Netsuite Transformer"
      transformer_service = TransformerService(transformer_sample_object['id'], self.dynamodb)
      update_transformer_response = transformer_service.update_transformer(transformer_sample_object, transformer_sample_object['id'])
      assert update_transformer_response['Attributes']['name'] == "Netsuite Transformer"

    def test_get_transformer_by_id(self):
      self.table.put_item(Item=transformer_sample_object)
      transformer_service = TransformerService(transformer_sample_object['id'], self.dynamodb)
      get_transformer_response = transformer_service.get_transformer_by_id()
      assert get_transformer_response['Item']['id'] == transformer_sample_object['id']
    
    def test_get_transformer_by_id_not_found(self):
      transformer_service = TransformerService(transformer_sample_object['id'], self.dynamodb)
      get_transformer_response = transformer_service.get_transformer_by_id()
      assert get_transformer_response == None
    
    def test_dynamodb_resource_not_defined(self):
      transformer_service = TransformerService(transformer_sample_object['id'])