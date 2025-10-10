from enum import IntEnum

class LabelEnum(IntEnum):
    def __new__(cls, value: int, label: str, description: str = ""): ...
    @classmethod
    def from_label(cls, label: str):
        """根据 label 查找枚举成员"""
    @classmethod
    def labels(cls) -> list[str]:
        """获取所有标签"""
    @property
    def label(self) -> str: ...
    @property
    def description(self) -> str: ...
