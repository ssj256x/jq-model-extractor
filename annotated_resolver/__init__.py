from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, get_origin, get_args

import jq
from pydantic import BaseModel


class Resolver(ABC):
    @abstractmethod
    def resolve(self, data: dict) -> Any | None:
        pass


class Transform:
    def __init__(self, fn, description: str = ""):
        self.fn = fn
        self.description = description

    def apply(self, data):
        return self.fn(data)


class Pipeline(Resolver):
    def __init__(self, base: Resolver, transforms: list[Transform]):
        self.base = base
        self.transforms = transforms

    def resolve(self, data: dict):
        value = self.base.resolve(data)
        for t in self.transforms:
            value = t.apply(value)
        return value


class JqMode(Enum):
    ONE = 'one'
    MANY = 'many'


class Jq(Resolver):
    def __init__(self, expression: str, *, mode: JqMode = JqMode.ONE):
        self.expression = expression
        self.mode = mode

    def resolve(self, data: dict) -> Any | None:
        result = jq.compile(self.expression).input_value(data).all()
        if not result:
            return None

        return result[0] if self.mode == JqMode.ONE else result


class Computed(Resolver):
    def __init__(self, fn: Callable[[dict], Any], *, description: str = ""):
        self.fn = fn
        self.description = description

    def resolve(self, data: dict):
        return self.fn(data)


def build_pipeline_from_field(field) -> Resolver | None:
    base_resolver: Resolver | None = None
    transforms: list[Transform] = []

    for meta in field.metadata:
        if isinstance(meta, Resolver):
            base_resolver = meta
        elif isinstance(meta, Transform):
            transforms.append(meta)

    if base_resolver is None:
        return None

    if transforms:
        return Pipeline(base_resolver, transforms)

    return base_resolver


def is_jq_model(_type) -> bool:
    return isinstance(_type, type) and issubclass(_type, JqModel)


def is_list_of_jq_model(tp):
    return (
            get_origin(tp) is list
            and is_jq_model(get_args(tp)[0])
    )


class JqModel(BaseModel):
    @classmethod
    def from_json(cls, data: dict[str, Any]):
        values = {}

        for field_name, field in cls.model_fields.items():
            field_type = field.annotation
            resolver: Resolver | None = build_pipeline_from_field(field)

            # In case a Pipeline exists
            if resolver:
                value = resolver.resolve(data)
                if is_list_of_jq_model(field_type) and value is not None:
                    model_cls = get_args(field_type)[0]
                    value = [model_cls.from_json(value) for value in value]
                values[field_name] = value
                continue

            if is_jq_model(field_type):
                values[field_name] = field_type.from_json(data)
                continue

            values[field_name] = None

        return cls(**values)
