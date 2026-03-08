from typing import get_origin, get_args

from .resolver import Resolver, Pipeline
from .transform import Transform


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
    from .model import JqModel
    return isinstance(_type, type) and issubclass(_type, JqModel)


def is_list_of_jq_model(tp):
    return (
            get_origin(tp) is list
            and is_jq_model(get_args(tp)[0])
    )
