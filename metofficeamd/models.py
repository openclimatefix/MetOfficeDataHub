from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Extent(BaseModel):
    t: List[datetime]
    z: List[int]


class OrderInfo(BaseModel):
    orderId: str 
    name: str
    modelId: str
    requiredLatestRuns: Optional[List[int]]
    format: str


class File(BaseModel):
    fileId: str
    runDateTime: datetime
    run: int


class OrderList(BaseModel):
    orders: List[OrderInfo] = []


class OrderDetails(BaseModel):
    order: OrderInfo
    files: List[File]


class RunDetails(BaseModel):
    run: int
    runDateTime: datetime
    runFilter: str


class RunListForModel(BaseModel):
    modelId: str
    completeRuns: List[RunDetails]


class RunList(BaseModel):
    runs: List[RunListForModel]


class ParameterDetails(BaseModel):
    parameterId: str
    extent: Extent


class FileDetails(BaseModel):
    parameterDetails: List[ParameterDetails]
    file: File
