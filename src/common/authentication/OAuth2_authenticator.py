from typing import Optional
from datetime import datetime
from aws_lambda_powertools.utilities.parser import BaseModel

class OAuth2Authenticate(BaseModel):
    id : Optional[str]
    access_token : str
    access_token_expiry_time :int
    refresh_token :str
    refresh_token_expiry_time :int
    token_type :str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]