""" This package talks with  Oauth authenticator Service"""
import json
from aws_lambda_powertools import Logger
from authentication.OAuth2_authenticator_service import OAuth2AuthenticatorService

from adapter.adapter_oauth_config_service import AdapterOAuthConfigService
logger = Logger(service="docuphase-ig-oauth2")

""" Class for Outh2 adapter Authenticator service. """
class AdapterOAuth2AuthenticatorService:
    """This class contains all required methods to get OAuth2"""
    def __init__(self, auth_id):
        self.__auth_id = auth_id

    def get_authorization_url(self):
        """Returns the authorization url"""
        auth_config_svc = AdapterOAuthConfigService(self.__auth_id)
        auth_config =  auth_config_svc.get_oauth_config_by_id()
        if auth_config['statusCode'] == 201:
            oauth_svc = OAuth2AuthenticatorService(auth_config['body']['authorize_url'],
                                                   auth_config['body']['callback_uri'],
                                                   auth_config['body']['client_id'],
                                                   auth_config['body']['client_secret'],
                                                   auth_config['body']['token_url'],
                                                   auth_config['body']['refresh_token_url'],
                                                   auth_config['body']['response_type'],
                                                   auth_config['body']['scope'],
                                                   auth_config['body']['state'])       

            redirect_url = oauth_svc.get_authorization_code_url()
            response = {
                   "statusCode": 201,
                    "body": json.dumps(redirect_url)
                    }
            return response
        return auth_config

    def get_access_token(self, auth_code):
        """Returns access token"""
        auth_config_svc = AdapterOAuthConfigService(self.__auth_id)
        auth_config =  auth_config_svc.get_oauth_config_by_id()
        oauth_svc = OAuth2AuthenticatorService(auth_config['body']['authorize_url'],
                                               auth_config['body']['callback_uri'],
                                               auth_config['body']['client_id'],
                                               auth_config['body']['client_secret'],
                                               auth_config['body']['token_url'],
                                               auth_config['body']['refresh_token_url'],
                                               auth_config['body']['response_type'],
                                               auth_config['body']['scope'],
                                               auth_config['body']['state'])       

        return oauth_svc.grant_app_login(auth_code)

        
        
