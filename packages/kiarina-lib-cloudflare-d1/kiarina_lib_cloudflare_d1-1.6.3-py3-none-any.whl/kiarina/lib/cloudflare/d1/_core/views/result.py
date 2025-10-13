from pydantic import BaseModel, ConfigDict

from .query_result import QueryResult


class Result(BaseModel):
    model_config = ConfigDict(extra="allow")

    success: bool

    result: list[QueryResult]

    @property
    def first(self) -> QueryResult:
        if not self.result:
            raise ValueError("No results available")

        return self.result[0]
