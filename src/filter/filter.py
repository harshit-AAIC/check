from typing import List, Optional
from aws_lambda_powertools.utilities.parser import BaseModel

class FilterCriteria(BaseModel):
    key: str
    value: str
    operator: str
    condition: str

class Filter(BaseModel):
    id: Optional[str]
    name: str
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]
    filter_criteria: List[FilterCriteria]
