from aws_lambda_powertools import Logger


logger = Logger(service="docuphase-ig-adapter")

class MicrosofGP():
    def __init__(self, corelation_id=None ):
        self.__corelation_id = corelation_id


    def do_create_customer(self, request_payload, access_token):
        logger.info(f"Performing Microsoft GP Adapter Create Vendor action"
                    f"{request_payload}{access_token} {self.__corelation_id}")
        # Call ERP
        res = {
                'statusCode': 201,
                'message': "ok"
            }
        return res
