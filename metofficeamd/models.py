""" Pydantic models for the return objects of the API """
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Extent(BaseModel):
    """Extent model"""

    t: List[datetime]
    z: List[int]


class OrderInfo(BaseModel):
    """Order info model"""

    orderId: str
    name: str
    modelId: str
    requiredLatestRuns: Optional[List[int]]
    format: str


class File(BaseModel):
    """File model"""

    fileId: str
    runDateTime: datetime
    run: int
    local_filename: Optional[str]
    timesteps: Optional[List[int]]


class OrderList(BaseModel):
    """Order list model"""

    orders: List[OrderInfo] = []


class OrderDetails(BaseModel):
    """Order details model"""

    order: OrderInfo
    files: List[File]


class RunDetails(BaseModel):
    """Run details model"""

    run: int
    runDateTime: datetime
    runFilter: str


class RunListForModel(BaseModel):
    """Run list for a specific model"""

    modelId: str
    completeRuns: List[RunDetails]


class RunList(BaseModel):
    """Run list model"""

    runs: List[RunListForModel]


class ParameterDetails(BaseModel):
    """Parameter details model"""

    parameterId: str
    extent: Extent


class FileDetails(BaseModel):
    """File details model"""

    parameterDetails: List[ParameterDetails]
    file: File
