from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.parser import ValidationError, parse, BaseModel, validator

logger = Logger(service="docuphase-ig-util")


### Check if key is None
def check_if_none(key, value):
    if value is None:
        logger.info("%s is None" % key)
        raise KeyError("%s is None" % key)
    return value

### Check if key is Empty
def check_if_empty(key, value):
    if not value:
        logger.info("%s is Empty" % key)
        raise KeyError("%s is Empty" % key)
    return value


def check_if_not_none(key, value):
    if value :
        logger.info("%s should not have any value" % key)
        raise KeyError("%s should not have any value" % key)
    return value
