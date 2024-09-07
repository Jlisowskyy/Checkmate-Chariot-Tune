from .GlobalModels import *


class TuneParameter(BaseModel):
    name: str
    min: int
    max: int


class TestDescription(BaseModel):
    name: str
    parameters: list[TuneParameter]
    commit: str
    passwordHash: str


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


class File(BaseModel):
    name: str
    content: str


class Backup(BaseModel):
    result: CommandResult
    backup: list[File]
