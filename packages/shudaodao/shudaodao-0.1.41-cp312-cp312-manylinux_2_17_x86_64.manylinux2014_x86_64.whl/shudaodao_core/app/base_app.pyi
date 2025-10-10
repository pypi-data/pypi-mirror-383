import abc
from ..auth.auth_router import AuthRouter as AuthRouter
from ..config.app_config import AppConfig as AppConfig
from ..config.schemas.routers import RouterConfigSetting as RouterConfigSetting
from ..license.verify import verify_license as verify_license
from ..logger.logging_ import logging as logging
from ..portal_auth import auth_registry as auth_registry
from ..portal_auth.entity_table.auth_user import (
    AuthRegister as AuthRegister,
    AuthUser as AuthUser,
)
from ..portal_enum import enum_registry as enum_registry
from ..services.auth_service import AuthService as AuthService
from ..services.casbin_service import PermissionService as PermissionService
from ..services.data_service import DataService as DataService
from ..services.db_engine_service import DBEngineService as DBEngineService
from ..tools.class_scaner import ClassScanner as ClassScanner
from ..tools.database_checker import DatabaseChecker as DatabaseChecker
from ..tools.tenant_checker import TenantManager as TenantManager
from ..utils.core_utils import CoreUtil as CoreUtil
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from fastapi import FastAPI

class BaseApplication(ABC, metaclass=abc.ABCMeta):
    """应用核心类，负责初始化和管理FastAPI应用。

    该类封装了FastAPI应用的完整生命周期，包括环境初始化、许可验证、数据库检查、
    路由加载、中间件配置、异常处理以及服务启动/关闭等流程。
    子类必须实现抽象方法以完成自定义初始化逻辑。
    """

    app: Incomplete
    def __init__(self) -> None:
        """初始化应用核心组件。

        执行顺序：
        1. 打印启动横幅
        2. 初始化环境信息日志
        3. 验证软件许可
        4. 初始化底层引擎（数据库、Redis等）
        5. 创建FastAPI实例
        6. 调用子类实现的 application_init() 配置中间件
        7. 加载路由
        8. 注册全局异常处理器
        """
    @abstractmethod
    def application_init(self, app: FastAPI) -> None:
        """子类必须实现：用于注册中间件、事件等FastAPI初始化逻辑。

        Args:
            app (FastAPI): 当前FastAPI应用实例。
        """
    @abstractmethod
    async def application_load(self):
        """子类必须实现：应用启动时加载自定义资源（如缓存预热、连接池等）。"""
    @abstractmethod
    async def application_unload(self):
        """子类必须实现：应用关闭时释放资源（如关闭连接、保存状态等）。"""
