""" This package implements Oauth authenticator. """
import requests, json
from aws_lambda_powertools import Logger

logger = Logger(service="docuphase-ig-authenticator")

""" Class for OAuth authentication with different adapters. """
class OAuth2AuthenticatorService:
    """Class init """

    def __init__(self, authorize_url, callback_uri, client_id, client_secret, token_url, refresh_token_url,
                 response_type='code', scope='rest_webservices',
                 state='ytv2XLx1BpT5Q0F3MRPHb9656323'):
        self.authorize_url = authorize_url
        self.callback_uri  = callback_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.response_type = response_type
        self.scope = scope
        self.state = state
        self.token_url = token_url
        self.refresh_token_url = refresh_token_url
        self.authorization_redirect_url = None

    def get_authorization_code_url(self):
        """Method to get authorization code"""
        logger.info(f"Getting authorization code redirect url")
        self.authorization_redirect_url = self.authorize_url + '?response_type=' + self.response_type + '&client_id=' + self.client_id + '&redirect_uri=' + self.callback_uri + '&scope=' + self.scope + '&state=' + self.state
        return self.authorization_redirect_url


    def grant_app_login(self, auth_code):
        """ Method to login using Oauth and get tokens. """
        logger.info(f"Getting access token and refresh token by using auth code {auth_code}")
        data = {'grant_type': 'authorization_code', 'code': auth_code, 'redirect_uri': self.callback_uri}
        logger.info(f"Calling {self.token_url} with data {data}")
        response = requests.post(self.token_url, data=data, verify=False, allow_redirects=False, auth=(self.client_id, self.client_secret))
        if response.status_code == 200:
            res = {
                "statusCode" : 200,
                "tokens" : json.loads(response.text)
            }
            return res
        
        logger.info(f"Oauth is failed with status code {response.status_code} and with {response.text} message")
        res = {
                "statusCode" : response.status_code,
                "body" : response.text
            }
        return res
        

    def get_new_access_token(self, refresh_token):
        """ Method to get new access token using the refresh token. """
        logger.info(f"Getting new access token by using existing refresh token")
        data = {'grant_type': 'refresh_token', 'refresh_token': refresh_token}
        logger.info(f"Get new access token by using url {self.refresh_token_url}"
                    f"using data {data}")
        response = requests.post(self.refresh_token_url, data=data, verify=False, allow_redirects=False, auth=(self.client_id, self.client_secret))
        if response.status_code == 200:
            logger.info(f"Successfully got new access by using refresh token with response"
                    "f {response} ")
            res = {
                "statusCode" : 200,
                "tokens" : json.loads(response.text)
            }
            return res
        
        logger.info(f"Getting new access token by using refresh token is failed with response"
                    f"{response}")
        res = {
                "statusCode" : response.status_code,
                "body" : response.text
            }
        return res
