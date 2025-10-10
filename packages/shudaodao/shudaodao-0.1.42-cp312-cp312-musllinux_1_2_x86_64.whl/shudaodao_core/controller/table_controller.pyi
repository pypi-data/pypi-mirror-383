from ..auth.auth_router import AuthRouter as AuthRouter
from ..type.var import (
    SQLModelCreate as SQLModelCreate,
    SQLModelDB as SQLModelDB,
    SQLModelResponse as SQLModelResponse,
    SQLModelUpdate as SQLModelUpdate,
)
from .generic_controller import GenericController as GenericController
from .router_config import RouterConfig as RouterConfig

class AuthController:
    """认证控制器工厂类。

    该类提供一个统一的工厂方法 `create`，用于快速生成带有权限控制（RBAC/ABAC）的 Restful API 控制器。
    它基于通用控制器 `GenericController` 封装，并结合 `AuthRouter` 实现路由注册与权限校验逻辑。
    支持对创建、读取、更新、删除、查询等操作分别配置路由行为与权限策略。

    适用于需要对数据库模型（SQLModel）快速暴露带权限验证接口的场景。
    """
    @classmethod
    def create(
        cls,
        *,
        model_class: type[SQLModelDB],
        create_schema: type[SQLModelCreate] = None,
        update_schema: type[SQLModelUpdate] = None,
        response_schema: type[SQLModelResponse],
        create_router: RouterConfig = None,
        update_router: RouterConfig = None,
        read_router: RouterConfig = None,
        delete_router: RouterConfig = None,
        query_router: RouterConfig = None,
        prefix: str | None = None,
        schema_name: str | None = None,
        table_name: str | None = None,
        tags: list | None = None,
        default_role: str | None = None,
        auth_role: str | None = None,
        auth_obj: str | None = None,
        auth_act: str | None = None,
        db_config_name: str | None = None,
    ):
        """
        创建一个带权限控制的控制器实例，并注册对应路由。

        该方法通过组合 `AuthRouter` 与 `GenericController`，为指定的数据模型自动生成标准
        CRUD+Q（查询）接口，并集成权限中间件。所有接口默认启用认证与授权，
        可通过 `RouterConfig` 精细控制各操作的行为。

        Args:
            model_class (Type[SQLModelDB]): 对应数据库表的 SQLModel 模型类（需继承自 SQLModelDB）。
            create_schema (Type[SQLModelCreate], optional): 创建数据时使用的 Pydantic 输入模型。
            update_schema (Type[SQLModelUpdate], optional): 更新数据时使用的 Pydantic 输入模型。
            response_schema (Type[SQLModelResponse]): 接口返回时使用的 Pydantic 输出模型。
            create_router (RouterConfig, optional): 创建操作的路由配置。若为 None，则使用默认配置。
            update_router (RouterConfig, optional): 更新操作的路由配置。若为 None，则使用默认配置。
            read_router (RouterConfig, optional): 单条读取操作的路由配置。若为 None，则使用默认配置。
            delete_router (RouterConfig, optional): 删除操作的路由配置。若为 None，则使用默认配置。
            query_router (RouterConfig, optional): 列表查询操作的路由配置。若为 None，则使用默认配置。
            prefix (str, optional): API 路由前缀。若未指定，将自动生成为 ``/v1/{schema_name}/{table_name}``。
            schema_name (str, optional): 逻辑模块名（如 "user", "order"），用于生成默认权限角色、对象名及标签。
            table_name (str, optional): 数据表名（或资源名），用于生成路由前缀和权限对象标识。
            tags (List[str], optional): OpenAPI 文档中的标签，用于分组接口。默认为 ``["{schema_name}.table"]``。
            default_role (str, optional): 默认角色名，用于角色定义并关联对象动作。默认为 ``schema_name``。
            auth_role (str, optional): 特定角色访问授权校验时使用的角色标识。默认为 None。
            auth_obj (str, optional): 权限校验时的操作对象（资源）标识。默认为 ``{schema_name}.{table_name}``。
            auth_act (str, optional): 全局默认的操作动作（如 "read"），但通常由各 RouterConfig 覆盖。
            db_config_name (str, optional): 指定使用的数据库配置名称。

        Returns:
            AuthRouter: 已配置并注册了所有操作路由的认证路由器实例，可用于挂载到 FastAPI 应用。

        Note:
            - 各 ``RouterConfig`` 实例若未显式设置 ``enabled=False``，则对应接口将被启用。
            - 权限字段（如 ``auth_role``, ``auth_obj``, ``auth_act``）支持在全局和单个路由级别分别配置，
              路由级别配置优先。
            - 自动生成的权限标识遵循 ``{schema}.{resource}`` 命名规范，便于 RBAC/ABAC 策略管理。
        """
