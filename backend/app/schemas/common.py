from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Error(CamelModel):
    detail: str
