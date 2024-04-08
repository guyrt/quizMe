from pydantic import BaseModel
from typing import List


class Column(BaseModel):
    name: str
    description: str
    dtype: str = ""


class Table(BaseModel):
    name: str
    description: str
    columns: List[Column]


class UserSchemaSchema(BaseModel):
    name: str
    description: str
    tables: List[Table]
