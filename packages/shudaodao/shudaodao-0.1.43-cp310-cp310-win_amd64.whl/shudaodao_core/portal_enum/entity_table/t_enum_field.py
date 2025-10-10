#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：Shudaodao Auto Generator
# @Software ：PyCharm
# @Date     ：2025/10/09 16:09:29
# @Desc     ：SQLModel classes for shudaodao_enum.t_enum_field

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import BigInteger, Text, Boolean
from sqlmodel import SQLModel, Relationship

from .. import RegistryModel, get_table_schema, get_foreign_schema
from ...sqlmodel_ext.field import Field
from ...schemas.response import BaseResponse
from ...utils.generate_unique_id import get_primary_id

if TYPE_CHECKING:
    from .t_enum_schema import TEnumSchema
    from .t_enum_value import TEnumValue


class TEnumField(RegistryModel, table=True):
    """ 数据库对象模型 """
    __tablename__ = "t_enum_field"
    __table_args__ = {"schema": get_table_schema(), "comment": "枚举字段表"}

    field_id: int = Field(default_factory=get_primary_id, primary_key=True, sa_type=BigInteger, description="字段内码")
    schema_id: int = Field(
        sa_type=BigInteger, description="分组内码", foreign_key=f"{get_foreign_schema()}t_enum_schema.schema_id")
    field_label: str = Field(max_length=50, description="字段标签")
    field_class: str = Field(max_length=50, description="字段类名")
    field_name: str = Field(max_length=50, description="字段列名")
    description: Optional[str] = Field(default=None, nullable=True, sa_type=Text, description="描述")
    sort_order: Optional[int] = Field(default=10, nullable=True, description="字段索引")
    is_active: Optional[bool] = Field(default=None, nullable=True, sa_type=Boolean, description="是否启用")
    create_by: Optional[str] = Field(default=None, max_length=50, nullable=True, description="创建人")
    create_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(), nullable=True, description="创建日期")
    update_by: Optional[str] = Field(default=None, max_length=50, nullable=True, description="修改人")
    update_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(), nullable=True, description="修改日期")
    # -- 外键 --> 父对象 --
    schema: "TEnumSchema" = Relationship(back_populates="enum_fields")
    # -- 外键 --> 子对象 --
    enum_values: list["TEnumValue"] = Relationship(back_populates="field")


class TEnumFieldBase(SQLModel):
    """ 创建、更新模型 共用字段 """
    group_id: int = Field(sa_type=BigInteger, description="分组内码")
    field_label: str = Field(max_length=50, description="字段标签")
    field_class: str = Field(max_length=50, description="字段类名")
    field_name: str = Field(max_length=50, description="字段列名")
    description: Optional[str] = Field(default=None, description="描述")
    sort_order: Optional[int] = Field(default=10, description="字段索引")
    is_active: Optional[bool] = Field(default=None, description="是否启用")


class TEnumFieldCreate(TEnumFieldBase):
    """ 前端创建模型 - 用于接口请求 """
    ...


class TEnumFieldUpdate(TEnumFieldBase):
    """ 前端更新模型 - 用于接口请求 """
    ...


class TEnumFieldResponse(BaseResponse):
    """ 前端响应模型 - 用于接口响应 """
    field_id: int = Field(description="字段内码", sa_type=BigInteger)
    group_id: int = Field(description="分组内码", sa_type=BigInteger)
    field_label: str = Field(description="字段标签")
    field_class: str = Field(description="字段类名")
    field_name: str = Field(description="字段列名")
    description: Optional[str] = Field(description="描述", default=None)
    sort_order: Optional[int] = Field(description="字段索引", default=None)
    is_active: Optional[bool] = Field(description="是否启用", default=None)
    create_by: Optional[str] = Field(description="创建人", default=None)
    create_at: Optional[datetime] = Field(description="创建日期", default=None)
    update_by: Optional[str] = Field(description="修改人", default=None)
    update_at: Optional[datetime] = Field(description="修改日期", default=None)
