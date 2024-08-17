from pydantic import BaseModel


class CommandResult(BaseModel):
    result: str
