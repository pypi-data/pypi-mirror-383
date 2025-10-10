from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    pass


class Provider(BaseModel):
    """A provider configuration for an AI Gateway."""

    name: str = Field(description="The name of the provider")
    uuid: str | None = Field(default=None, description="The UUID of the provider")
    api_base: str | None = Field(
        default=None, description="The base URL of the model provider API", validation_alias="apiBase"
    )
    api_key: str | None = Field(default=None, description="The API key for the provider", validation_alias="apiKey")


class ModelEndpoint(BaseModel):
    """A model endpoint configuration for an AI Gateway."""

    model_alias: str = Field(description="The model alias used by clients", validation_alias="modelAlias")
    model: str = Field(description="The actual model name on the provider")
    provider_name: str = Field(description="The name of the provider to use", validation_alias="providerName")
    weight: float | None = Field(default=1.0, description="Weight for load balancing")

    model_config = ConfigDict(protected_namespaces=())


class Gateway(BaseModel):
    """An AI Gateway instance."""

    name: str = Field(description="The name of the gateway")
    uuid: str | None = Field(default=None, description="The UUID of the gateway")
    description: str | None = Field(default=None, description="Description of the gateway")
    logging: bool = Field(default=True, description="Whether logging is enabled")
    providers: list[Provider] = Field(description="List of providers for this gateway")
    model_list: list[ModelEndpoint] = Field(description="List of model endpoints", validation_alias="modelList")

    model_config = ConfigDict(protected_namespaces=())
