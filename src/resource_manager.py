# -*- coding: utf-8 -*-
"""资源管理器 - Web 版，返回静态资源 URL"""

class ResourceManager:
    """资源管理器，提供静态资源 URL"""

    STATIC_PREFIX = "/static"

    def get_bubu_avatar(self, mode: str, size: int = 40) -> str:
        """获取布布头像 URL"""
        if mode == "survival":
            return f"{self.STATIC_PREFIX}/avatars/bubu_survival.png"
        return f"{self.STATIC_PREFIX}/avatars/bubu_roast.png"

    def get_yier_avatar(self, size: int = 40) -> str:
        """获取一二头像 URL"""
        return f"{self.STATIC_PREFIX}/avatars/yier.png"

    def get_icon(self, name: str) -> str:
        """获取图标 URL"""
        return f"{self.STATIC_PREFIX}/icons/{name}.svg"


_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器实例"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
