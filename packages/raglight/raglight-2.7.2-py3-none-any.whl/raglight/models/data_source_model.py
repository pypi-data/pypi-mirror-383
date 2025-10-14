from pydantic import BaseModel, Field
from typing import Union, Literal


class FolderSource(BaseModel):
    type: Literal["folder"] = "folder"
    path: str


class GitHubSource(BaseModel):
    type: Literal["github"] = "github"
    url: str
    branch: str = Field(default="main")


DataSource = Union[FolderSource, GitHubSource]
