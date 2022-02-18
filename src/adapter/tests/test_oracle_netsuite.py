import os
from unittest.mock import patch, Mock

import unittest
import uuid

from moto import mock_dynamodb2
from aws_lambda_powertools import Logger

from adapter.adapter_factory import AdapterFactory


logger = Logger(service="docuphase-ig-adapter")

@mock_dynamodb2
class OracleNetsuiteTest(unittest.TestCase):
    def setUp(self):
        os.environ['ORACLE_NETSUITE_BASE_URL'] = "https://TSTDRV1667270.suitetalk.api.netsuite.com"

    @patch('requests.post')
    def test_do_create_purchase_order_to_vendor_bill_success(self, mocked_post):
        mocked_post.return_value = Mock(status_code=204)
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_create_purchase_order_to_vendor_bill(request_json, access_token)
        assert result['statusCode'] == 201

    @patch('requests.post')
    def test_do_create_purchase_order_to_vendor_bill_failed(self, mocked_post):
        mocked_post.return_value = Mock(status_code=400)
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_create_purchase_order_to_vendor_bill(request_json, access_token)
        assert result['statusCode'] == 400

    @patch('requests.post')
    def test_do_create_purchase_order_to_vendor_bill_unothorized(self, mocked_post):
        mocked_post.return_value = Mock(status_code=401)
        request_json = { "entityid": "New Customer", "companyname": "My Company", "subsidiary": { "id": "1" } }
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_create_purchase_order_to_vendor_bill(request_json, access_token)
        assert result['statusCode'] == 401


    @patch('requests.get')
    def test_do_get_customer_success(self, mocked_get):
        mocked_get.return_value = Mock(status_code=200)
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_get_customer('123', access_token)
        assert result['statusCode'] == 200

    @patch('requests.get')
    def test_do_get_expense_report_success(self, mocked_get):
        mocked_get.return_value = Mock(status_code=200)
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_get_expense_report('123', access_token)
        assert result['statusCode'] == 200

    @patch('requests.get')
    def test_do_do_get_expense_report_failed(self, mocked_get):
        mocked_get.return_value = Mock(status_code=400)
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_get_expense_report('000', access_token)
        assert result['statusCode'] == 400

    @patch('requests.get')
    def test_do_get_expense_report_unothorized(self, mocked_get):
        mocked_get.return_value = Mock(status_code=401)
        access_token = 'thisis accesstoken'
        adapter_object = AdapterFactory.get_adapter_object("oracleNetsuite", str(uuid.uuid1()))
        result = adapter_object.do_get_expense_report('123', access_token)
        assert result['statusCode'] == 401