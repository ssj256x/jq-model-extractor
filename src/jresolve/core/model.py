from pydantic import BaseModel
from result import Result, Ok, Err
from typing import Any, get_args

from .helpers import is_jq_model, build_pipeline_from_field, is_list_of_jq_model
from .resolver import Resolver
from ..exceptions import ModelResolutionError, ResolutionError


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