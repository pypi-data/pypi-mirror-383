from .. import RegistryModel as RegistryModel, get_table_schema as get_table_schema
from ...schemas.response import BaseResponse as BaseResponse
from ...sqlmodel_ext.field import Field as Field
from ...utils.generate_unique_id import get_primary_id as get_primary_id
from .t_enum_field import TEnumField as TEnumField
from _typeshed import Incomplete
from datetime import datetime
from sqlmodel import SQLModel

class TEnumSchema(RegistryModel, table=True):
    """数据库对象模型"""

    __tablename__: str
    __table_args__: Incomplete
    schema_id: int
    schema_label: str
    schema_name: str
    sort_order: int | None
    description: str | None
    create_by: str | None
    create_at: datetime | None
    update_by: str | None
    update_at: datetime | None
    tenant_id: int | None
    enum_fields: list["TEnumField"]

class TEnumSchemaBase(SQLModel):
    """创建、更新模型 共用字段"""

    schema_label: str
    schema_name: str
    sort_order: int | None
    description: str | None

class TEnumSchemaCreate(TEnumSchemaBase):
    """前端创建模型 - 用于接口请求"""

class TEnumSchemaUpdate(TEnumSchemaBase):
    """前端更新模型 - 用于接口请求"""

class TEnumSchemaResponse(BaseResponse):
    """前端响应模型 - 用于接口响应"""

    schema_id: int
    schema_label: str
    schema_name: str
    sort_order: int | None
    description: str | None
    create_by: str | None
    create_at: datetime | None
    update_by: str | None
    update_at: datetime | None
