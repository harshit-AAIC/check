from aws_lambda_powertools import Logger

from adapter.oracle_netsuite import OracleNetsuite
from adapter.microsoft_gp import MicrosofGP
from adapter.adapter_constant import (ORACLE_NETSUITE, MICROSOFT_GP)

logger = Logger(service="docuphase-ig-adapter")

class AdapterFactory:

    @staticmethod
    def get_adapter_object(adapter_type, corelation_id):
        if adapter_type == ORACLE_NETSUITE:
            logger.info(f"Creating Oracle NetSuite object for given {adapter_type}"
                        f"with Execution ID ---> {corelation_id}")
            return OracleNetsuite(corelation_id)
        if adapter_type == MICROSOFT_GP:
            logger.info(f"Creating MicroSoftGP NetSuite object for given {adapter_type}"
                        f"with Execution ID ---> {corelation_id}")
            return MicrosofGP(corelation_id)
        logger.info("No adapter found for the given type {adapter_type}")
        return None
