# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["OrderSendForEmployeeResponse", "UnionMember0", "UnionMember1", "UnionMember1OrderResult"]


class UnionMember0(BaseModel):
    order_id: str = FieldInfo(alias="orderId")

    order_number: str = FieldInfo(alias="orderNumber")

    success: Literal[True]

    message: Optional[str] = None


class UnionMember1OrderResult(BaseModel):
    order_id: str = FieldInfo(alias="orderId")

    order_number: str = FieldInfo(alias="orderNumber")

    provider_id: str = FieldInfo(alias="providerId")


class UnionMember1(BaseModel):
    order_results: List[UnionMember1OrderResult] = FieldInfo(alias="orderResults")

    status: Literal["split"]

    success: Literal[True]

    message: Optional[str] = None


OrderSendForEmployeeResponse: TypeAlias = Union[UnionMember0, UnionMember1]
