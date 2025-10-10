from .. import (
    RegistryModel as RegistryModel,
    get_foreign_schema as get_foreign_schema,
    get_table_schema as get_table_schema,
)
from ...schemas.response import BaseResponse as BaseResponse
from ...sqlmodel_ext.field import Field as Field
from ...utils.generate_unique_id import get_primary_id as get_primary_id
from .t_enum_schema import TEnumSchema as TEnumSchema
from .t_enum_value import TEnumValue as TEnumValue
from _typeshed import Incomplete
from datetime import datetime
from sqlmodel import SQLModel

class TEnumField(RegistryModel, table=True):
    """数据库对象模型"""

    __tablename__: str
    __table_args__: Incomplete
    field_id: int
    schema_id: int
    field_label: str
    field_class: str
    field_name: str
    description: str | None
    sort_order: int | None
    is_active: bool | None
    create_by: str | None
    create_at: datetime | None
    update_by: str | None
    update_at: datetime | None
    schema: TEnumSchema
    enum_values: list["TEnumValue"]

class TEnumFieldBase(SQLModel):
    """创建、更新模型 共用字段"""

    group_id: int
    field_label: str
    field_class: str
    field_name: str
    description: str | None
    sort_order: int | None
    is_active: bool | None

class TEnumFieldCreate(TEnumFieldBase):
    """前端创建模型 - 用于接口请求"""

class TEnumFieldUpdate(TEnumFieldBase):
    """前端更新模型 - 用于接口请求"""

class TEnumFieldResponse(BaseResponse):
    """前端响应模型 - 用于接口响应"""

    field_id: int
    group_id: int
    field_label: str
    field_class: str
    field_name: str
    description: str | None
    sort_order: int | None
    is_active: bool | None
    create_by: str | None
    create_at: datetime | None
    update_by: str | None
    update_at: datetime | None
