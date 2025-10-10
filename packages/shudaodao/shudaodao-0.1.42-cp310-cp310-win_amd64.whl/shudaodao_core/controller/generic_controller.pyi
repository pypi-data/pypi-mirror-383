from ..auth.auth_router import AuthRouter as AuthRouter
from ..schemas.query_request import QueryRequest as QueryRequest
from ..services.data_service import DataService as DataService
from ..type.var import (
    SQLModelCreate as SQLModelCreate,
    SQLModelDB as SQLModelDB,
    SQLModelResponse as SQLModelResponse,
    SQLModelUpdate as SQLModelUpdate,
)
from ..utils.response_utils import ResponseUtil as ResponseUtil
from .router_config import RouterConfig as RouterConfig
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSession
from typing import Generic

class GenericController(
    Generic[SQLModelDB, SQLModelCreate, SQLModelUpdate, SQLModelResponse]
):
    """泛型路由控制器基类，自动注册标准 CRUD 与分页查询路由。

    该类通过泛型参数绑定数据模型与 Schema，结合 `RouterConfig` 控制各操作的启用状态、
    权限策略和响应消息，实现“声明式”资源控制器。

    泛型参数说明：
        SQLModelDB: 对应数据库模型类（继承自 SQLModel）。
        SQLModelCreate: 用于创建资源的请求 Schema。
        SQLModelUpdate: 用于更新资源的请求 Schema。
        SQLModelResponse: 用于响应的输出 Schema（通常排除敏感字段）。

    路由注册行为：
        - 每个操作（create/read/update/delete/query）是否注册，由对应的 `RouterConfig.enabled` 控制；
        - 所有路由均挂载到传入的 `AuthRouter` 实例上；
        - 权限控制（auth/auth_role/auth_obj/auth_act）由 `RouterConfig` 提供；
        - 数据操作委托给 `DataService`，响应统一由 `ResponseUtil` 包装。
    """
    def __init__(
        self,
        *,
        auth_router: AuthRouter,
        model_class: type[SQLModelDB],
        create_schema: type[SQLModelCreate],
        update_schema: type[SQLModelUpdate],
        response_schema: type[SQLModelResponse],
        create_router: RouterConfig,
        update_router: RouterConfig,
        read_router: RouterConfig,
        delete_router: RouterConfig,
        query_router: RouterConfig,
    ) -> None:
        """初始化泛型控制器并自动注册路由。

        Args:
            auth_router (AuthRouter): 已配置的认证路由容器，所有子路由将注册到此实例。
            model_class (Type[SQLModelDB]): 数据库模型类。
            create_schema (Type[SQLModelCreate]): 创建请求的 Pydantic 模型。
            update_schema (Type[SQLModelUpdate]): 更新请求的 Pydantic 模型。
            response_schema (Type[SQLModelResponse]): 响应返回的 Pydantic 模型。

            create_router (RouterConfig): 创建操作的路由配置。
            update_router (RouterConfig): 更新操作的路由配置。
            read_router (RouterConfig): 读取单个资源的路由配置。
            delete_router (RouterConfig): 删除操作的路由配置。
            query_router (RouterConfig): 分页/条件查询操作的路由配置。
        """
