import json


class ResponseClass():
    def __init__(self, headers):
        self.headers = headers

    def not_implimented_error(self):
        NOT_IMPLEMENTED_ERROR_RESPONSE = {
            'statusCode': 501,
            'body': json.dumps('Input parameters is missing')
        }
        return NOT_IMPLEMENTED_ERROR_RESPONSE

    def not_found_response(self):
        NOT_FOUND_RESPONSE = {
            "statusCode": 404,
            "body": json.dumps('Item not Found'),
            "headers": self.headers
        }
        return NOT_FOUND_RESPONSE

    def invalid_token_response(headers):
        INVALID_TOKEN_RESPONSE = {
            'statusCode': 401,
            'body': json.dumps('Invalid token'),
            'headers': headers
        }
        return INVALID_TOKEN_RESPONSE

    def created_successfully(headers):
        CREATED_SUCCESSFULLY = {
            'statusCode': 201,
            'body': json.dumps('Record created successfully'),
            'headers': headers
        }
        return CREATED_SUCCESSFULLY

    def bad_request(headers):
        BAD_REQUEST_RESPONSE = {
            'statusCode': 400,
            'body': json.dumps('Invalid input'),
            'headers': headers
        }
        return BAD_REQUEST_RESPONSE

    def search_successful(headers):
        FOUND_RESPONSE = {
            'statusCode': 200,
            'body': json.dumps('Record found successfully'),
            'headers': headers
        }
        return FOUND_RESPONSE

    def filter_failed(headers):
        FILTER_FAILED_RESPONSE = {
            'statusCode': 400,
            'body': json.dumps('Filter condition does not satisfied'),
            'headers': headers
        }
        return FILTER_FAILED_RESPONSE
