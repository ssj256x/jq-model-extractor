import jq


def full_name(data: dict) -> str:
    parts = [
        jq.compile('.profile.name.first').input_value(data).all()[0],
        jq.compile('.profile.name.middle').input_value(data).all()[0],
        jq.compile('.profile.name.last').input_value(data).all()[0]
    ]

    return " ".join(p for p in parts if p)
