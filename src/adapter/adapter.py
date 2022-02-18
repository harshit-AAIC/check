from typing import Optional, List
from datetime import datetime
from aws_lambda_powertools.utilities.parser import BaseModel


class AdapterAction(BaseModel):
    # id: str
    name: str
    input_attributes: dict
    function_name: str


class Adapter(BaseModel):
    # pylint disable=too-few-public-methods
    id: Optional[str]
    name: str
    status: str
    list_of_actions: List[AdapterAction]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    type: str
    which_auth_mechanism: str
    what_auth_id: str


class AdapterOauth(BaseModel):
    id: Optional[str]
    adapter_id: str
    client_id: str
    client_secret: str
    callback_uri: str
    redirect_uri: str
    token_url: str
    authorize_url: str
    scope: str
    state: str
    response_type: str
    refresh_token_url: str
