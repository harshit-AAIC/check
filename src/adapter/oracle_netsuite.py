
import json
import os

import requests
from aws_lambda_powertools import Logger

from adapter.oracle_restapi_constant import (CREATE_CUSTOMER,
                                             CREATE_PURCHASE_ORDER_VENDOR_BILL,
                                             GET_CUSTOMER, GET_EXPENSE_REPORT)

logger = Logger(service="docuphase-ig-oracle-netsuite-adapter")


class OracleNetsuite():
    def __init__(self, corelation_id=None):
        self.__corelation_id = corelation_id
        self.__base_url = os.getenv('ORACLE_NETSUITE_BASE_URL')

    def do_create_customer(self, request_payload, access_token):
        logger.info(
            f"Create Customer with Execution Id --->  {self.__corelation_id}")
        auth_token = 'Bearer' + ' ' + access_token
        headers = {"Authorization": auth_token,
                   "Content-Type": "application/json"}
        logger.info(f"Rest api endpoints to create customer {self.__base_url + CREATE_CUSTOMER}"
                    f"with request json {json.dumps(request_payload)}"
                    f"with Excecution Id {self.__corelation_id}")
        res = requests.post(self.__base_url + CREATE_CUSTOMER,
                            data=json.dumps(request_payload), headers=headers)
        logger.info(f"Response from Rest Endpoint ---> {res}")
        if res.status_code == 204:
            res = {
                'statusCode': 201,
                'body': json.dumps('Record inserted successfully')
            }
            logger.info(f"Successfully inserted record Response is {res}"
                        f"with Excecution Id {self.__corelation_id}")
            return res
        res = {
            'statusCode': res.status_code,
            'body': res.text
        }
        logger.info(f"Error ocurred while inserting record {res}"
                    f"with Excecution Id {self.__corelation_id}")
        return res

    def do_get_customer(self, param, access_token):
        logger.info(f"Performing Oracle Netsuite Adapter get Customer action for customer {param} "
                    f"with Execution Id  {self.__corelation_id}")
        auth_token = 'Bearer' + ' ' + access_token
        headers = {"Authorization": auth_token,
                   "Content-Type": "application/json"}
        res = requests.get(self.__base_url + GET_CUSTOMER + '/'
                           + param, headers=headers, cookies=None, auth=None, timeout=None)
        logger.info(f"Response from Rest Endpoint ---> {res}")
        if res.status_code == 200:
            res = {
                'statusCode': res.status_code,
                'body': res.text
            }
            return res
        res = {
            'statusCode': res.status_code,
            'body': res.text
        }
        return res

    def do_create_purchase_order_to_vendor_bill(self, request_payload, access_token):
        """REST API CALL for create purchase order to vendor bill"""
        logger.info(
            f"Create Purchase Order to vendor Bill with Execution Id --->  {self.__corelation_id}")
        auth_token = 'Bearer' + ' ' + access_token
        headers = {"Authorization": auth_token,
                   "Content-Type": "application/json"}
        res = requests.post(self.__base_url +
                            CREATE_PURCHASE_ORDER_VENDOR_BILL, data=json.dumps(request_payload), headers=headers)
        logger.info(f"Response from Rest Endpoint ---> {res}")
        if res.status_code == 204:
            res = {
                'statusCode': 201,
                'body': res.text
            }
            return res
        res = {
            'statusCode': res.status_code,
            'body': res.text
        }
        return res

    def do_get_expense_report(self, param, access_token):
        """REST API CALL to get expense report"""
        logger.info(
            f"Get Expense Report for Customer --->  {self.__corelation_id}")
        auth_token = 'Bearer' + ' ' + access_token
        headers = {"Authorization": auth_token,
                   "Content-Type": "application/json"}
        res = requests.get(self.__base_url +
                           GET_EXPENSE_REPORT + '/'
                           + param, headers=headers, cookies=None, auth=None, timeout=None)
        logger.info(f"Response from Rest Endpoint ---> {res}")
        if res.status_code == 200:
            res = {
                'statusCode': res.status_code,
                'body': json.dumps('Record inserted successfully')
            }
            return res
        res = {
            'statusCode': res.status_code,
            'body': res.text
        }
        return res
