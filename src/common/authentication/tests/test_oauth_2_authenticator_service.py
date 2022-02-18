import unittest
from unittest.mock import patch, Mock
from moto import mock_dynamodb2

from aws_lambda_powertools import Logger
from common.authentication.OAuth2_authenticator_service import OAuth2AuthenticatorService


logger = Logger(service="docuphase-ig-adapter")


AUTHORIZE_URL = "https://TSTDRV1667270.app.netsuite.com/app/login/oauth2/authorize.nl"
TOKEN_URL = "https://TSTDRV1667270.suitetalk.api.netsuite.com/services/rest/auth/oauth2/v1/token"

CLIENT_ID = 'c5dccdfc2d982200dae248ef31f4c9eb32baf8b28489368d276c619c107e5904'
CLIENT_SECRET = '0471bbc710bf7428d49d5b572772af35c34a9fb91a118fd7c1e3084e0d9b36e0'
CALLBACK_URL = "https://oauth.pstmn.io/v1/browser-callback"
AUTH_CONFIG = {
                'id' : '1234-abcd-5678-ghty',
                'mechanism': 'OAuth2',
                'client_id': '12234fdgsgd',
                'client_secret' : 'ghjklouytedcssnbvx',
                'callback_uri' : 'https://google.com',
                'token_url': 'https://1234.netsuite.com/v1/token',
                'authorize_url': 'https://1234.netsuite.com/v1/app/login/oauth2/authorize.nl',
                'scope' : 'rest_webservices',
                'state': 'ykv2XLx1BpT5Q0F3MRPHb9656323',
                'response_type': 'code',
                'refresh_token_url':'https://1234.netsuite.com/v1/token'
                
            }

@mock_dynamodb2
class OAuth2AuthenticatorServiceTest(unittest.TestCase):
    """Test Cases for Oauth2 service"""
    @patch('requests.post')
    def test_get_access_token_failed(self, mocked_post):
        mocked_post.return_value = Mock(status_code=403, text= '{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')

        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'],
                                               AUTH_CONFIG['scope'],
                                               AUTH_CONFIG['state'])       

        code  = 'ad45e31c7440516daf33cd4b20e898b6'
        access_tokens = oauth_svc.grant_app_login(code)
        assert access_tokens['statusCode'] == 403

    @patch('requests.post')
    def test_get_access_token_success(self, mocked_post):
        mocked_post.return_value = Mock(status_code=200, text= '{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')

        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'],
                                               AUTH_CONFIG['scope'],
                                               AUTH_CONFIG['state'])       

        code  = 'ad45e31c7440516daf33c39b09157026b81acd326bebfb2dafd32d4b20e898b6'
        access_tokens = oauth_svc.grant_app_login(code)
        assert access_tokens['statusCode'] == 200
    
    @patch('requests.post')
    def test_get_access_token_server_error(self, mocked_post):
        mocked_post.return_value = Mock(status_code=500, text= '{"access_token": \
                "thisisacccesstoken","refresh_token":"thisisrefreshtoken", \
                    "expires_in":"3600","token_type":"Bearer"}')

        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'],
                                               AUTH_CONFIG['scope'],
                                               AUTH_CONFIG['state'])       

        code  = 'ad45e31c7440516daf33c39b09157026b81acd326bebfb2dafd32d4b20e898b6'
        access_tokens = oauth_svc.grant_app_login(code)
        assert access_tokens['statusCode'] == 500





    @patch('requests.post')
    def test_get_access_token_using_refresh_token_failed(self, mocked_post):
        mocked_post.return_value = Mock(status_code=403, text= '{"access_token": \
                "updated_token","refresh_token":"updated_token", \
                    "expires_in":"3600","token_type":"Bearer"}')

        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'],
                                               AUTH_CONFIG['scope'],
                                               AUTH_CONFIG['state'])       

        access_tokens = oauth_svc.get_new_access_token('thisisrefrestoken')
        assert access_tokens['statusCode'] == 403

    @patch('requests.post')
    def test_get_access_token_using_refresh_token_success(self, mocked_post):
        mocked_post.return_value = Mock(status_code=200, text= '{"access_token": \
                "updated_token","refresh_token":"updated_token", \
                    "expires_in":"3600","token_type":"Bearer"}')

        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'],
                                               AUTH_CONFIG['scope'],
                                               AUTH_CONFIG['state'])       

        access_tokens = oauth_svc.get_new_access_token('thisisrefrestoken')
        assert access_tokens['statusCode'] == 200
        assert access_tokens['tokens']['refresh_token'] == 'updated_token'
    
    @patch('requests.post')
    def test_get_access_token_using_refresh_token_server_error(self, mocked_post):
        mocked_post.return_value = Mock(status_code=500, text= '{"access_token": \
                "updated_token","refresh_token":"updated_token", \
                    "expires_in":"3600","token_type":"Bearer"}')

        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'], 
                                               AUTH_CONFIG['scope'],
                                               AUTH_CONFIG['state'])       

        access_tokens = oauth_svc.get_new_access_token('thisisrefrestoken')
        assert access_tokens['statusCode'] == 500



    def test_get_authorization_url(self):
        oauth_svc = OAuth2AuthenticatorService(AUTH_CONFIG['authorize_url'],
                                               AUTH_CONFIG['callback_uri'],
                                               AUTH_CONFIG['client_id'],
                                               AUTH_CONFIG['client_secret'],
                                               AUTH_CONFIG['token_url'],
                                               AUTH_CONFIG['refresh_token_url'],
                                               AUTH_CONFIG['response_type'],
                                               AUTH_CONFIG['scope'], AUTH_CONFIG['state'])       

        url = oauth_svc.get_authorization_code_url()
        assert url is not None
