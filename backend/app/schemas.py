from pydantic import BaseModel, Field
from enum import Enum


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class EndpointBase(BaseModel):
    endpoint_path: str = Field(..., description="The API endpoint path, e.g. /users/{id}")
    http_method: HttpMethod = Field(..., description="HTTP verb for this endpoint")
    source_file: str = Field(..., description="Relative path of the file this endpoint was parsed from")
    is_deprecated: bool = Field(False, description="Whether the endpoint is marked deprecated in its spec")


class EndpointCreate(EndpointBase):
    pass


class EndpointRead(EndpointBase):
    id: int

    model_config = {"from_attributes": True}


class ScanRequest(BaseModel):
    repo_url: str = Field(..., description="HTTPS URL of the GitHub/GitLab repository to scan")
    token: str = Field(..., description="Personal access token for private repo access")


class ScanResponse(BaseModel):
    endpoints_discovered: int
    endpoints: list[EndpointRead]
