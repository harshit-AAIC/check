import json
import os
import traceback


def cors_headers(event):
    try:
        ALLOWED_ORIGINS = [
            'http://localhost:3000/',
            # '*'
        ]

        if not eval(os.environ['DISABLE_CORS']):
            origin = event.get('headers').get('origin') if event.get(
                'headers').get('origin') else event.get('headers').get('Origin')
            if origin in ALLOWED_ORIGINS:
                headers = {
                    'Access-Control-Allow-Origin': origin,
                    'Access-Control-Allow-Credentials': True,
                }
        else:
            headers = {
                'Access-Control-Allow-Origin': '*'
            }
        return headers
    except:
        traceback.print_exc()
        return False
