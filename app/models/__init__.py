from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Callable, List, Annotated

import jq
from pydantic import BaseModel


class JqMode(Enum):
    ONE = "one"
    MANY = "many"


class Transform:
    def __init__(self, fn, description: str = ""):
        self.fn = fn
        self.description = description

    def apply(self, data):
        return self.fn(data)


class Resolver(ABC):
    @abstractmethod
    def resolve(self, data: dict):
        pass


class Computed(Resolver):
    def __init__(self, *, fn: Callable[[dict], Any], description: str = ""):
        self.fn = fn
        self.description = description

    def resolve(self, data: dict):
        return self.fn(data)


class Pipeline(Resolver):
    def __init__(self, base: Resolver, transforms: List[Transform]):
        self.base = base
        self.transforms = transforms

    def resolve(self, data: dict):
        value = self.base.resolve(data)
        for transform in self.transforms:
            value = transform.apply(value)
        return value


class Jq:
    def __init__(self, expression: str, *, mode: JqMode = JqMode.ONE):
        self.expression = expression
        self.mode = mode

    def extract(self, data: dict) -> dict | None:
        result = jq.compile(self.expression).input_value(data).all()
        if not result:
            return None

        return result[0] if self.mode == JqMode.ONE else result


class JqModel(BaseModel):

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        values = {}

        for field_name, field in cls.model_fields.items():
            default_value = field.default

            match default_value:
                case Jq():
                    values[field_name] = default_value.extract(data)
                case Computed():
                    values[field_name] = default_value.resolve(data)
                case _:
                    values[field_name] = None

        return cls(**values)
