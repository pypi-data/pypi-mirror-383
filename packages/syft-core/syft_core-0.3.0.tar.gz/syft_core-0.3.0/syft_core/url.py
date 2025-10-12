import re
from pathlib import Path
from typing import Any, Dict, Union
from urllib.parse import urlencode, urlparse

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, ValidationInfo
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing_extensions import Self

from syft_core.types import PathLike, to_path
from syft_core.workspace import SyftWorkspace


class SyftBoxURL(str):
    def __new__(cls, url: str):
        instance = super().__new__(cls, url)
        if not cls.is_valid(url):
            raise ValueError(f"Invalid SyftBoxURL: {url}")
        instance.parsed = urlparse(url)
        return instance

    @classmethod
    def is_valid(cls, url: str) -> bool:
        """Validates the given URL matches the syft:// protocol and email-based schema."""
        pattern = r"^syft://([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(/.*)?$"
        return bool(re.match(pattern, url))

    @property
    def query(self) -> Dict[str, str]:
        """Returns the query parameters as a dictionary."""
        if not self.parsed.query:
            return {}

        return dict(
            param.split("=", 1)
            for param in self.parsed.query.split("&")
            if "=" in param
        )

    @property
    def protocol(self) -> str:
        """Returns the protocol (syft://)."""
        return self.parsed.scheme + "://"

    @property
    def host(self) -> str:
        """Returns the host, which is the email part."""
        return self.parsed.netloc

    @property
    def path(self) -> str:
        """Returns the path component after the email."""
        return self.parsed.path

    def to_local_path(self, datasites_path: PathLike) -> Path:
        """
        Converts the SyftBoxURL to a local file system path.

        Args:
            datasites_path (Path): Base directory for datasites.

        Returns:
            Path: Local file system path.
        """
        # Remove the protocol and prepend the datasites_path
        local_path = to_path(datasites_path) / self.host / self.path.lstrip("/")
        return local_path.resolve()

    def as_http_params(self) -> Dict[str, str]:
        return {
            "method": "get",
            "datasite": self.host,
            "path": self.path,
        }

    def to_http_get(self, rpc_url: str) -> str:
        rpc_url = rpc_url.split("//")[-1]
        params = self.as_http_params()
        url_params = urlencode(params)
        http_url = f"http://{rpc_url}?{url_params}"
        return http_url

    @classmethod
    def from_path(cls, path: PathLike, workspace: SyftWorkspace) -> Self:
        rel_path = to_path(path).relative_to(workspace.datasites)
        # convert to posix path to make it work on Windows OS
        rel_path = rel_path.as_posix()
        return cls(f"syft://{rel_path}")

    @classmethod
    def validate(
        cls, value: Union["SyftBoxURL", str], info: ValidationInfo
    ) -> "SyftBoxURL":
        if type(value) not in (str, cls):
            raise ValueError(
                f"Invalid type for url: {type(value)}. Expected str or SyftBoxURL."
            )
        value = str(value)
        if not cls.is_valid(value):
            raise ValueError(f"Invalid SyftBoxURL: {value}")
        return cls(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Pydantic V2 core schema for custom type validation."""
        return core_schema.with_info_after_validator_function(
            cls.validate,
            handler(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema_or_field: Any, schema_handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Define the JSON schema representation for Pydantic models."""
        return {
            "type": "string",
            "format": "uri",
            "description": "A SyftBox URL",
        }
