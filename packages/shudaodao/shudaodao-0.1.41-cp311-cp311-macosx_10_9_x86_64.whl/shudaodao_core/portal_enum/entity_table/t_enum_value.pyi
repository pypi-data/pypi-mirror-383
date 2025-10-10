from .. import (
    RegistryModel as RegistryModel,
    get_foreign_schema as get_foreign_schema,
    get_table_schema as get_table_schema,
)
from ...schemas.response import BaseResponse as BaseResponse
from ...sqlmodel_ext.field import Field as Field
from ...utils.generate_unique_id import get_primary_id as get_primary_id
from .t_enum_field import TEnumField as TEnumField
from _typeshed import Incomplete
from datetime import datetime
from sqlmodel import SQLModel

class TEnumValue(RegistryModel, table=True):
    """数据库对象模型"""

    __tablename__: str
    __table_args__: Incomplete
    enum_id: int
    field_id: int
    enum_pid: int
    enum_label: str
    enum_name: str
    enum_value: int
    sort_order: int | None
    is_active: bool | None
    description: str | None
    create_by: str | None
    create_at: datetime | None
    update_by: str | None
    update_at: datetime | None
    field: TEnumField

class TEnumValueBase(SQLModel):
    """创建、更新模型 共用字段"""

    field_id: int
    enum_pid: int
    enum_label: str
    enum_name: str
    enum_value: int
    sort_order: int | None
    is_active: bool | None
    description: str | None

class TEnumValueCreate(TEnumValueBase):
    """前端创建模型 - 用于接口请求"""

class TEnumValueUpdate(TEnumValueBase):
    """前端更新模型 - 用于接口请求"""

class TEnumValueResponse(BaseResponse):
    """前端响应模型 - 用于接口响应"""

    enum_id: int
    field_id: int
    enum_pid: int
    enum_label: str
    enum_name: str
    enum_value: int
    sort_order: int | None
    is_active: bool | None
    description: str | None
    create_by: str | None
    create_at: datetime | None
    update_by: str | None
    update_at: datetime | None
