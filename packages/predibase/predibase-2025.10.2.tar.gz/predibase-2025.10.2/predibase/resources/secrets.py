from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from predibase import Predibase


class Secrets:
    def __init__(self, client: Predibase):
        self._client = client
        self._session = client._session

    @staticmethod
    def _validate_key(key: Any) -> str:
        if not isinstance(key, str):
            raise ValueError(f"{key} is not a valid secret key. Secret keys are required to be strings.")

    @staticmethod
    def _validate_value(key: str, value: Any) -> str:
        if not isinstance(value, str):
            raise ValueError(
                f"{value} is not a valid value for secret {key}. Secret values are required to be strings.",
            )

    def get(self, key: str) -> str:
        self._validate_key(key)
        return self._client.http_get("/v2/secrets", json={"key": key})["value"]

    def create(self, key: str, value: str) -> None:
        self._validate_key(key)
        self._validate_value(key, value)
        self._client.http_post("/v2/secrets", json={"key": key, "value": value})

    def update(self, key: str, value: str) -> None:
        self._validate_key(key)
        self._validate_value(key, value)
        self._client.http_put("/v2/secrets", json={"key": key, "value": value})

    def delete(self, key: str) -> None:
        self._validate_key(key)
        self._client.http_delete("/v2/secrets", json={"key": key})
