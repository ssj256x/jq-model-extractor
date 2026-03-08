from abc import ABC, abstractmethod
from enum import Enum
from result import Result, Ok, Err
from typing import Any, Callable, get_origin, get_args

import jq
from pydantic import BaseModel

from annotated_resolver.exceptions import (
    ResolutionError,
    JqResolutionError,
    ComputationError,
    TransformError,
    ModelResolutionError,
    MissingValueError
)


class Resolver(ABC):
    @abstractmethod
    def resolve(self, data: dict) -> Result[Any, ResolutionError]:
        pass


class Transform:
    def __init__(self, fn, description: str = ""):
        self.fn = fn
        self.description = description

    def apply(self, data):
        try:
            return Ok(self.fn(data))
        except Exception as e:
            return Err(TransformError(str(e)))


class Pipeline(Resolver):
    def __init__(self, base: Resolver, transforms: list[Transform]):
        self.base = base
        self.transforms = transforms

    def resolve(self, data: dict):
        result = self.base.resolve(data)

        for transform in self.transforms:
            if result.is_err():
                return result

            result = transform.apply(result.ok())

        return result


class JqMode(Enum):
    ONE = 'one'
    MANY = 'many'


class Jq(Resolver):
    def __init__(self, expression: str, *, mode: JqMode = JqMode.ONE, required: bool = False):
        self.expression = expression
        self.mode = mode
        self.required = required
        self.program = jq.compile(expression)

    def resolve(self, data: dict) -> Any | None:
        try:
            result = self.program.input_value(data).all()
            value = result[0] if self.mode == JqMode.ONE else result

            if not value:
                if self.required:
                    return Err(MissingValueError(self.expression))
                return Ok(None)

            # value = result[0] if self.mode == JqMode.ONE else result
            return Ok(value)
        except Exception as e:
            return Err(JqResolutionError(str(e)))


class Computed(Resolver):
    def __init__(self, fn: Callable[[dict], Any], *, description: str = ""):
        self.fn = fn
        self.description = description

    def resolve(self, data: dict):
        try:
            return Ok(self.fn(data))
        except Exception as e:
            return Err(ComputationError(str(e)))


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
    def from_json(cls, data: dict[str, Any]) -> Result[Any, ResolutionError]:
        values: dict[str, Any] = {}
        errors: dict[str, ResolutionError] = {}

        for field_name, field in cls.model_fields.items():
            field_type = field.annotation
            resolver: Resolver | None = build_pipeline_from_field(field)

            # Case 1: Resolver / Pipeline Exists
            if resolver:
                result = resolver.resolve(data)
                if result.is_err():
                    errors[field_name] = result.err()
                    continue

                value = result.ok()

                # Handle list[JqModel]
                if is_list_of_jq_model(field_type) and value is not None:
                    model_cls = get_args(field_type)[0]

                    resolved_items = []
                    for idx, item in enumerate(value):
                        nested_result = model_cls.from_json(item)
                        if nested_result.is_err():
                            errors[f"{field_name}[{idx}]"] = nested_result.err()
                            continue

                        resolved_items.append(nested_result.ok())

                    value = resolved_items

                values[field_name] = value
                continue

            if is_jq_model(field_type):
                nested_result = field_type.from_json(data)
                if nested_result.is_err():
                    errors[field_name] = nested_result.err()
                    continue

                values[field_name] = nested_result.ok()
                continue

            values[field_name] = None

        if errors:
            return Err(ModelResolutionError(errors))

        try:
            model = cls(**values)
            return Ok(model)
        except Exception as e:
            return Err(ModelResolutionError({"model": e}))
