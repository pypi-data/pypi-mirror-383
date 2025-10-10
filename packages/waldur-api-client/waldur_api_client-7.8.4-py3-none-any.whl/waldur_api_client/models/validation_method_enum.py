from enum import Enum


class ValidationMethodEnum(str, Enum):
    ARIREGISTER = "ariregister"

    def __str__(self) -> str:
        return str(self.value)
