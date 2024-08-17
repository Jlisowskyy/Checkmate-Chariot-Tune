from pydantic import BaseModel


class TuneParameter(BaseModel):
    name: str
    min: int
    max: int


class TestDescription(BaseModel):
    name: str
    parameters: list[TuneParameter]
    commit: str
    passwordHash: str


class CommandResult(BaseModel):
    resultCode: int


class AuthInfo(BaseModel):
    passwordHash: str


class TestInfo(BaseModel):
    result: CommandResult
    tests: list[TestDescription]


class TestAccessInfo(BaseModel):
    auth: AuthInfo
    name: str


class TestResults(BaseModel):
    result: CommandResult
    parameters: list[int]
