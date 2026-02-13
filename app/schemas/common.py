# from typing import Generic, TypeVar, Optional
# from pydantic import BaseModel, Field
# from pydantic.generics import GenericModel
# import time
# import uuid

# T = TypeVar("T")

# class BaseAPIResponse(GenericModel, Generic[T]):
#     tid: str = Field(default_factory=lambda: uuid.uuid4().hex)
#     result: Optional[T] = None
#     t: int = Field(default_factory=lambda: int(time.time() * 1000))
#     success: bool = True
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field
import time
import uuid

T = TypeVar("T")

class BaseAPIResponse(BaseModel, Generic[T]):
    tid: str = Field(default_factory=lambda: uuid.uuid4().hex)
    result: Optional[T] = None
    t: int = Field(default_factory=lambda: int(time.time() * 1000))
    success: bool = True
