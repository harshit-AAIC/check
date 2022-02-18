from datetime import datetime
from typing import List, Optional

from aws_lambda_powertools.utilities.parser import BaseModel


class FlowStep(BaseModel):
    order: str
    action_name: str
    filter_id: str
    before_transformer_id: str
    adapter_id: str
    after_transformer_id: str


class Flow(BaseModel):
    flow_id: Optional[str]
    name: str
    desc: str
    status: str
    flow_url: Optional[str]
    adapter_img: str
    flowstep: List[FlowStep]
    auth_id : str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class FlowExecutionModel(BaseModel):
    flow_id: str
    execution_id: str
    status : str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    


# print(Flow.schema())  #using this method will print the the model schema,
                        # it should help in visualizing the expected input
# print(Flow.schema())
    # @validator('name')
    # def is_not_none(self, var):
    #   if var is None:
    #      raise ValueError("name cannot be empty")
    # return var
