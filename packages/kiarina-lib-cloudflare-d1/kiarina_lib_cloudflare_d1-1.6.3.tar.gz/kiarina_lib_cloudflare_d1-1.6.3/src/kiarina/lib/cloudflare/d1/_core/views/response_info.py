from pydantic import BaseModel, ConfigDict


class ResponseInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: int

    message: str
