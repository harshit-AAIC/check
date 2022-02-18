from typing import Optional
from datetime import datetime

from aws_lambda_powertools.utilities.parser import BaseModel

class Transformer(BaseModel):
    #pylint disable=too-few-public-methods
    id: Optional[str]
    name: str
    status: str
    input_payload: dict
    mapping_payload: dict
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
