from abc import ABC, abstractmethod
from enum import Enum

import jq
from result import Result, Ok, Err
from typing import Any, Callable

from .transform import Transform
from ..exceptions import (
    ResolutionError,
    JqResolutionError,
    ComputationError,
    MissingValueError
)


class Resolver(ABC):
    @abstractmethod
    def resolve(self, data: dict) -> Result[Any, ResolutionError]:
        pass


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
