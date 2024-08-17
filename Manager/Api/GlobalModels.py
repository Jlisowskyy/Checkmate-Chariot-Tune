from pydantic import BaseModel


class CommandResult(BaseModel):
    resultCode: int
