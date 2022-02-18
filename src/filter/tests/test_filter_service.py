import json
import os
import unittest
import boto3
from moto import mock_dynamodb2
from aws_lambda_powertools import Logger

from filter.filter_service import FilterService

logger = Logger(service="docuphase-ig-filter")

@mock_dynamodb2
class FilterServiceTest(unittest.TestCase):

        def setUp(self):
            """
            Create database resource and mock table
            """
            os.environ['AWS_REGION'] = "us-east-1"
            os.environ['FILTER_TABLE'] = "filter-table"
            os.environ['DISABLE_CORS'] = "True"  
            self.dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            self.table = self.dynamodb.create_table(
                TableName=os.environ['FILTER_TABLE'],
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

        def test_apply_filter_with_condition_equal_to(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "EQUAL TO",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "India",
                "condition": "equal to", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': 42, 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

            
        def test_apply_filter_with_and_operator(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "AND OPERATOR",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "India",
                "condition": "equal to", "operator": "and"},
                {"key": "state", "value": "Maharashtra",
                "condition": "equal to", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload,"83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_or_operator(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "OR OPERATOR",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "India",
                "condition": "equal to", "operator": "or"},
                {"key": "state", "value": "Tamil Nadu",
                "condition": "equal to", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload,"83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True


        def test_apply_filter_with_condition_contains(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION CONTAINS",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "in",
                "condition": "contains", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload,"83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_haskey(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION HAS KEY",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "",
                "condition": "has key", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload,"83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_startswith(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION STARTSWITH",
            "status": "Created",
            "filter_criteria": [{"key": "subject", "value": "Hel",
                "condition": "startswith", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_endswith(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION ENDSWITH",
            "status": "Created",
            "filter_criteria": [{"key": "subject", "value": "ld!",
                "condition": "endswith", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_not_equal_to(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION NOT EQUAL TO",
            "status": "Created",
            "filter_criteria": [{"key": "city", "value": "Mumbai",
                "condition": "not equal to", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_does_not_contain(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION DOES NOT CONTAIN",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "US",
                "condition": "does not contain", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_greater_than(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "GREATER THAN",
            "status": "Created",
            "filter_criteria": [{"key": "id1", "value": 30,
                "condition": "greater than", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': 42, 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_condition_less_than(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "LESS THAN",
            "status": "Created",
            "filter_criteria": [{"key": "id1", "value": 50,
                "condition": "less than", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': 42, 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True


        def test_apply_filter_with_condition_startswith_negative(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION STARTSWITH",
            "status": "Created",
            "filter_criteria": [{"key": "subject", "value": "hel",
                "condition": "startswith", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
                'country': 'India', 'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result == False


        def test_apply_filter_with_key_does_not_exist_with_not_equal_to(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION NOT EQUAL TO",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "US",
                "condition": "not equal to", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
            'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is True

        def test_apply_filter_with_key_does_not_exist_with_equal_to(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION NOT EQUAL TO",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "US",
                "condition": "equal to", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
            'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result == False

        def test_apply_filter_with_key_does_not_exist_with_does_not_contain(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION DOES NOT CONTAIN",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "US",
                "condition": "does not contain", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
            'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result == False

        def test_apply_filter_with_key_does_not_exist_with_contains(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION CONTAINS",
            "status": "Created",
            "filter_criteria": [{"key": "country", "value": "US",
                "condition": "contains", "operator": ""}
        ]
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
            'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result == False

        def test_apply_filter_with_filter_criteria_missing(self):
            get_payload = {
            "id": "17hus-78uht-89jfc",
            "name": "CONDITION CONTAINS",
            "status": "Created"
        }
            docuphase_payload= {'id1': '42', 'subject': 'Hello, world!',
            'state': 'Maharashtra', 'city': 'Pune'}

            dynamodb = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])
            table = dynamodb.Table(os.environ['FILTER_TABLE'])
            event_str = json.dumps(get_payload)
            item = json.loads(event_str)
            table.put_item(Item=item)
            filter_service= FilterService('17hus-78uht-89jfc')

            result = filter_service.apply_filter_result(docuphase_payload, "83e71c16-4912-11ec-a1a5-9a22ed39fc71")
            assert result is None


            
