from __future__ import annotations

from typing import TYPE_CHECKING

from predibase.config import GatewayConfig, UpdateGatewayConfig, ProviderConfig, ModelEndpointConfig
from predibase.resources.gateway import Gateway

if TYPE_CHECKING:
    from predibase import Predibase


class Gateways:
    """Collection class for managing AI Gateways."""

    def __init__(self, client: Predibase):
        self._client = client
        self._session = client._session

    def create(self, gateway_config: GatewayConfig) -> Gateway:
        """Create a new AI Gateway.

        Args:
            gateway_config: Configuration for the gateway including providers and models

        Returns:
            Gateway: The created gateway instance

        Example:
            >>> from predibase import Predibase, GatewayConfig, ProviderConfig, ModelEndpointConfig
            >>> pb = Predibase()
            >>>
            >>> config = GatewayConfig(
            ...     name="my-openai-gateway",
            ...     description="Gateway for OpenAI models",
            ...     providers=[
            ...         ProviderConfig(
            ...             name="openai",
            ...             api_base="https://api.openai.com/v1",
            ...             api_key="sk-..."
            ...         )
            ...     ],
            ...     model_list=[
            ...         ModelEndpointConfig(
            ...             model_alias="gpt-4",
            ...             model="gpt-4",
            ...             provider_name="openai"
            ...         )
            ...     ]
            ... )
            >>> gateway = pb.gateways.create(config)
        """
        providers = []
        for provider in gateway_config.providers:
            if isinstance(provider, ProviderConfig):
                provider = provider.model_dump(
                    exclude_none=True,
                    by_alias=True,
                )
            providers.append(provider)

        model_list = []
        for model in gateway_config.model_list:
            if isinstance(model, ModelEndpointConfig):
                model = model.model_dump(
                    exclude_none=True,
                    by_alias=True,
                )
            model_list.append(model)

        # Convert the config to the API format
        payload = {
            "name": gateway_config.name,
            "description": gateway_config.description,
            "logging": gateway_config.logging,
            "providers": providers,
            "modelList": model_list,
        }

        response = self._client.http_post("/v2/gateways", json=payload)
        return Gateway.model_validate(response)

    def delete(self, name: str) -> None:
        """Delete an AI Gateway by name.

        Args:
            name: The name of the gateway to delete

        Example:
            >>> pb = Predibase()
            >>> pb.gateways.delete("my-openai-gateway")
        """
        self._client.http_delete(f"/v2/gateways/{name}")

    def get(self, name: str) -> Gateway:
        """Get an AI Gateway by name.

        Args:
            name: The name of the gateway to retrieve

        Returns:
            Gateway: The gateway instance

        Example:
            >>> pb = Predibase()
            >>> gateway = pb.gateways.get("my-openai-gateway")
        """
        response = self._client.http_get(f"/v2/gateways/{name}")
        return Gateway.model_validate(response["data"])

    def list(
        self, name_filter: str | None = None, limit: int | None = None, offset: int | None = None
    ) -> list[Gateway]:
        """List AI Gateways with optional filtering and pagination.

        Args:
            name_filter: Optional filter to search for gateways by name (case-insensitive substring match)
            limit: Maximum number of gateways to return (default: 50)
            offset: Number of gateways to skip for pagination (default: 0)

        Returns:
            list[Gateway]: List of gateways matching the criteria

        Example:
            >>> pb = Predibase()
            >>> # List all gateways
            >>> all_gateways = pb.gateways.list()
            >>>
            >>> # Search for gateways with "openai" in the name
            >>> openai_gateways = pb.gateways.list(name_filter="openai")
            >>>
            >>> # Get first 10 gateways
            >>> first_10 = pb.gateways.list(limit=10, offset=0)
        """
        params = {}
        if name_filter is not None:
            params["name"] = name_filter
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        response = self._client.http_get("/v2/gateways", params=params)
        gateways_data = response["data"]["gateways"]

        # Handle case where gateways might be None
        if gateways_data is None:
            return []

        return [Gateway.model_validate(gateway) for gateway in gateways_data]

    def update(self, name: str, update_config: UpdateGatewayConfig) -> Gateway:
        """Update an AI Gateway.

        Args:
            name: The name of the gateway to update
            update_config: Configuration specifying what to update

        Returns:
            Gateway: The updated gateway instance

        Example:
            >>> from predibase import Predibase, UpdateGatewayConfig, ProviderConfig
            >>> pb = Predibase()
            >>>
            >>> # Add a new provider
            >>> update_config = UpdateGatewayConfig(
            ...     add_providers=[
            ...         ProviderConfig(
            ...             name="anthropic",
            ...             api_base="https://api.anthropic.com/v1",
            ...             api_key="sk-ant-..."
            ...         )
            ...     ]
            ... )
            >>> gateway = pb.gateways.update("my-gateway", update_config)
            >>>
            >>> # Remove a specific model
            >>> from predibase import RemoveModelConfig
            >>> update_config = UpdateGatewayConfig(
            ...     remove_models=[
            ...         RemoveModelConfig(
            ...             model_alias="gpt-4",
            ...             provider_name="openai",
            ...             model="gpt-4"
            ...         )
            ...     ]
            ... )
            >>> gateway = pb.gateways.update("my-gateway", update_config)
            >>>
            >>> # Replace all providers
            >>> update_config = UpdateGatewayConfig(
            ...     providers=[
            ...         ProviderConfig(name="openai", api_base="...", api_key="...")
            ...     ]
            ... )
            >>> gateway = pb.gateways.update("my-gateway", update_config)
        """
        # Convert the config to the API format
        payload = {}

        # Basic properties
        if update_config.description is not None:
            payload["description"] = update_config.description
        if update_config.logging is not None:
            payload["logging"] = update_config.logging

        # Complete replacement
        if update_config.providers is not None:
            payload["providers"] = [
                {
                    "name": provider.name,
                    "apiBase": provider.api_base,
                    "apiKey": provider.api_key,
                }
                for provider in update_config.providers
            ]
        if update_config.model_list is not None:
            payload["modelList"] = [
                {
                    "modelAlias": model.model_alias,
                    "model": model.model,
                    "providerName": model.provider_name,
                    "weight": model.weight,
                }
                for model in update_config.model_list
            ]

        # Granular operations
        if update_config.add_providers is not None:
            payload["addProviders"] = [
                {
                    "name": provider.name,
                    "apiBase": provider.api_base,
                    "apiKey": provider.api_key,
                }
                for provider in update_config.add_providers
            ]
        if update_config.remove_providers is not None:
            payload["removeProviders"] = update_config.remove_providers

        if update_config.add_models is not None:
            payload["addModels"] = [
                {
                    "modelAlias": model.model_alias,
                    "model": model.model,
                    "providerName": model.provider_name,
                    "weight": model.weight,
                }
                for model in update_config.add_models
            ]
        if update_config.remove_models is not None:
            payload["removeModels"] = [
                {
                    "modelAlias": remove_model.model_alias,
                    "providerName": remove_model.provider_name,
                    "model": remove_model.model,
                }
                for remove_model in update_config.remove_models
            ]

        response = self._client.http_put(f"/v2/gateways/{name}", json=payload)
        return Gateway.model_validate(response["data"])
