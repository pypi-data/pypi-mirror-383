from __future__ import annotations

import ast
import base64
import inspect
from functools import cached_property
from typing import Any, Callable, Literal, TYPE_CHECKING

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    PositiveFloat,
    PositiveInt,
)

from predibase.resources.validation import ValidatedDict

if TYPE_CHECKING:
    pass


class ProviderConfig(BaseModel):
    """Configuration for an AI Gateway provider."""

    name: str = Field(description="The name of the provider")
    api_base: str | None = Field(
        default=None, description="The base URL of the model provider API", serialization_alias="apiBase"
    )
    api_key: str | None = Field(
        default=None, description="The API key for authenticating with the provider", serialization_alias="apiKey"
    )
    azure_openai_config: AzureOpenAIConfig | None = Field(
        default=None,
        description="Specific configurations to an Azure OpenAI provider",
        serialization_alias="azureOpenAIConfig",
    )
    aws_bedrock_config: AWSBedrockConfig | None = Field(
        default=None,
        description="Specific configurations to an AWS Bedrock provider",
        serialization_alias="awsBedrockConfig",
    )


class AWSBedrockConfig(BaseModel):
    aws_access_key_id: str | None = Field(
        description="The AWS access key ID for authentication", serialization_alias="awsAccessKeyId"
    )
    aws_secret_access_key: str | None = Field(
        description="The AWS secret access key for authentication", serialization_alias="awsSecretAccessKey"
    )
    aws_role_name: str | None = Field(
        default=None, description="The AWS role name to assume for authentication", serialization_alias="awsRoleName"
    )
    aws_bedrock_runtime_endpoint: str | None = Field(
        default=None,
        description="The AWS Bedrock runtime endpoint URL",
        serialization_alias="awsBedrockRuntimeEndpoint",
    )
    aws_region_name: str | None = Field(
        default=None, description="The AWS region name", serialization_alias="awsRegionName"
    )


class AzureOpenAIConfig(BaseModel):
    api_version: str | None = Field(
        description="The API version to be used for the Azure OpenAI API", serialization_alias="apiVersion"
    )


class ModelEndpointConfig(BaseModel):
    """Configuration for a model endpoint in an AI Gateway."""

    model_alias: str = Field(description="The model alias used by clients", serialization_alias="modelAlias")
    model: str = Field(description="The actual model name on the provider")
    provider_name: str = Field(description="The name of the provider to use", serialization_alias="providerName")
    weight: float | None = Field(default=1.0, description="Weight for load balancing")

    model_config = ConfigDict(protected_namespaces=())


class RemoveModelConfig(BaseModel):
    """Configuration for removing a specific model endpoint."""

    model_alias: str = Field(description="The model alias to remove")
    provider_name: str = Field(description="The provider name for the model to remove")
    model: str = Field(description="The actual model name to remove")

    model_config = ConfigDict(protected_namespaces=())


class GatewayConfig(BaseModel):
    """Configuration for creating an AI Gateway."""

    name: str = Field(description="The name of the gateway")
    description: str | None = Field(default=None, description="Description of the gateway")
    logging: bool = Field(default=False, description="Whether to enable request/response logging")
    providers: list[ProviderConfig] = Field(description="List of providers for this gateway")
    model_list: list[ModelEndpointConfig] = Field(description="List of model endpoints")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, protected_namespaces=())


class UpdateGatewayConfig(BaseModel):
    """Configuration for updating an AI Gateway.

    All fields are optional.
    """

    description: str | None = Field(default=None, description="Updated description")
    logging: bool | None = Field(default=None, description="Whether to enable logging")

    # Complete replacement options
    providers: list[ProviderConfig] | None = Field(default=None, description="Replace all providers")
    model_list: list[ModelEndpointConfig] | None = Field(default=None, description="Replace all models")

    # Granular update options
    add_providers: list[ProviderConfig] | None = Field(default=None, description="Providers to add")
    remove_providers: list[str] | None = Field(default=None, description="Provider names to remove")
    add_models: list[ModelEndpointConfig] | None = Field(default=None, description="Models to add")
    remove_models: list[RemoveModelConfig] | None = Field(default=None, description="Specific models to remove")

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, protected_namespaces=())


class SamplingParamsConfig(BaseModel):
    temperature: float | None = Field(default=None)
    top_p: float | None = Field(default=None)
    top_k: int | None = Field(default=None)
    max_tokens: int | None = Field(default=None)


class FinetuningConfig(BaseModel):
    # This is required in most cases, but coded as optional for continued training.
    base_model: str | None = Field(default=None)

    adapter: str | None = Field(default=None)
    task: Literal["sft", "continued_pretraining", "grpo"] | None = Field(default="sft")
    epochs: int | None = Field(default=None)
    train_steps: int | None = Field(default=None)
    learning_rate: float | None = Field(default=None)
    rank: int | None = Field(default=None)
    target_modules: list[str] | None = Field(default=None)
    enable_early_stopping: bool | None = Field(default=None)
    apply_chat_template: bool | None = Field(default=None)
    lr_scheduler: dict | None = Field(default=None)
    optimizer: dict | None = Field(default=None)
    lora_alpha: PositiveInt | None = Field(default=None)
    lora_dropout: PositiveFloat | None = Field(default=None)
    warmup_ratio: PositiveFloat | None = Field(default=None)
    effective_batch_size: PositiveInt | None = Field(default=None)


class SFTConfig(FinetuningConfig):
    task: Literal["sft"] = "sft"


class ContinuedPretrainingConfig(FinetuningConfig):
    task: Literal["continued_pretraining"] = "continued_pretraining"


class GRPOConfig(FinetuningConfig):
    task: Literal["grpo"] = "grpo"
    beta: float | None = Field(default=None)
    num_generations: int | None = Field(default=None)
    sampling_params: SamplingParamsConfig | None = Field(default=None)
    reward_fns: RewardFunctionsConfig | None = Field(
        default=None,
        serialization_alias="rewardFns",
        validation_alias=AliasChoices("rewardFns", "reward_fns"),
    )
    secrets: dict[str, str] | None = Field(default=None)

    @field_validator("reward_fns", mode="before")
    @classmethod
    def convert_callable_list(cls, val: Any) -> Any:
        if not isinstance(val, list):
            return val

        return RewardFunctionsConfig(functions=val)

    @field_validator("secrets", mode="before")
    @classmethod
    def convert_secrets(cls, val: Any) -> Any:
        if not isinstance(val, dict):
            return val

        return {k: str(v) for k, v in val.items()}


def get_task_type(cfg: FinetuningConfig, default: str = "sft") -> str:
    if isinstance(cfg, dict):
        return str(cfg.get("task", default))

    return cfg.task


class ClassificationConfig(FinetuningConfig):
    task: Literal["classification"] = "classification"


class RewardFunctionsConfig(BaseModel, validate_assignment=True):
    runtime: RewardFunctionsRuntimeConfig | None = Field(default=None)
    functions: dict[str, RewardFunction] = Field(default_factory=dict)

    @field_validator("functions", mode="before")
    @classmethod
    def convert_callable_list(cls, val: Any) -> Any:
        if not isinstance(val, list):
            return val

        return {f.__name__: RewardFunction.from_callable(f) for f in val}

    @field_validator("functions", mode="after")
    @classmethod
    def convert_to_validated_dict(cls, val: dict[str, RewardFunction]) -> dict[str, RewardFunction]:
        return ValidatedDict(str, RewardFunction, val)

    def __setitem__(self, key: str, value: Callable | RewardFunction):
        if not isinstance(key, str):
            raise ValueError(f"expected key to be a string - got {type(key)}")

        if not isinstance(value, Callable) and not isinstance(value, RewardFunction):
            raise ValueError(f"expected value to be a callable or RewardFunction object - got {type(value)}")

        self.functions[key] = value

    def __getitem__(self, key: str):
        return self.functions[key]

    def __delitem__(self, key: str):
        return self.functions.__delitem__(key)


class RewardFunctionsRuntimeConfig(BaseModel):
    packages: list[str] | None = Field(default=None)


class RewardFunction(BaseModel):
    encoded_fn: str = Field(serialization_alias="encodedFn", validation_alias=AliasChoices("encodedFn", "encoded_fn"))

    def __repr__(self):
        encoded_fn_snippet = f"{self.encoded_fn[:30]}..." if len(self.encoded_fn) >= 30 else self.encoded_fn
        return f"RewardFunction(encoded_fn='{encoded_fn_snippet}')"

    @model_validator(mode="before")
    @classmethod
    def coerce_from_callable(cls, val: Any) -> Any:
        if isinstance(val, Callable):
            # NOTE: the call to model_dump is necessary - see
            # https://github.com/pydantic/pydantic/issues/9336#issuecomment-2082419008
            val = RewardFunction.from_callable(val).model_dump()

        return val

    @classmethod
    def from_callable(cls, fn: Callable) -> RewardFunction:
        fn_name = getattr(fn, "__name__", None)
        if not fn_name:
            raise ValueError("Input is not a function or is missing a name")

        if not inspect.isfunction(fn):
            raise ValueError("Expected input to be a function")

        params = inspect.signature(fn).parameters
        if len(params) != 3:
            raise ValueError(f"unexpected number of arguments for input - expected 3, " f"found {len(params)}")

        fn_source = inspect.getsource(fn)
        return RewardFunction(encoded_fn=base64.b64encode(fn_source.encode("utf-8")).decode("utf-8"))

    @cached_property
    def source(self):
        return base64.b64decode(self.encoded_fn).decode("utf-8")

    @cached_property
    def function(self):
        ast_root = ast.parse(self.source)

        # Check that the input is a single function definition
        if len(ast_root.body) != 1 or not isinstance(ast_root.body[0], ast.FunctionDef):
            raise ValueError("Expected encoded data to be a Python function")

        # Render the function locally
        exec(compile(ast_root, filename="<string>", mode="exec"))

        return locals()[ast_root.body[0].name]


class ServingComputeSpec(BaseModel):
    requests: ServingComputeRequests
    region: str | None = Field(default=None)


class ServingComputeRequests(BaseModel):
    inference: ComputeRequest


class ComputeRequest(BaseModel):
    sku: str


class UpdateDeploymentConfig(BaseModel):
    # Note: necessary because this particular model and its children are used to both deserialize and serialize data.
    # Other models in this SDK are used exclusively for deserializing data to a Python object that is never (for now)
    # reserialized back to the API for a different request.
    model_config = ConfigDict(populate_by_name=True)

    base_model: str | None = Field(
        default=None,
        validation_alias="baseModel",
        serialization_alias="baseModel",
    )
    custom_args: list[str] | None = Field(
        default=None,
        validation_alias="customArgs",
        serialization_alias="customArgs",
    )
    cooldown_time: int | None = Field(
        default=None,
        validation_alias="cooldownTime",
        serialization_alias="cooldownTime",
    )
    hf_token: str | None = Field(
        default=None,
        validation_alias="hfToken",
        serialization_alias="hfToken",
    )
    min_replicas: int | None = Field(
        default=None,
        validation_alias="minReplicas",
        serialization_alias="minReplicas",
    )
    max_replicas: int | None = Field(
        default=None,
        validation_alias="maxReplicas",
        serialization_alias="maxReplicas",
    )
    scale_up_threshold: int | None = Field(
        default=None,
        validation_alias="scaleUpRequestThreshold",
        serialization_alias="scaleUpRequestThreshold",
    )
    max_total_tokens: int | None = Field(
        default=None,
        validation_alias="maxTotalTokens",
        serialization_alias="maxTotalTokens",
    )
    lorax_image_tag: str | None = Field(
        default=None,
        validation_alias="loraxImageTag",
        serialization_alias="loraxImageTag",
    )
    request_logging_enabled: bool | None = Field(
        default=None,
        validation_alias="requestLoggingEnabled",
        serialization_alias="requestLoggingEnabled",
    )
    direct_ingress: bool | None = Field(
        default=None,
        validation_alias="directIngress",
        serialization_alias="directIngress",
    )
    preloaded_adapters: list[str] | None = Field(
        default=None,
        validation_alias="preloadedAdapters",
        serialization_alias="preloadedAdapters",
    )
    speculator: str | None = Field(
        default=None,
        validation_alias="speculator",
        serialization_alias="speculator",
    )
    prefix_caching: bool | None = Field(
        default=None,
        validation_alias="prefixCaching",
        serialization_alias="prefixCaching",
    )
    backend: Literal["v1", "v2", "v3"] | None = Field(
        default=None,
        validation_alias="backend",
        serialization_alias="backend",
    )
    disable_adapters: bool | None = Field(
        default=None,
        validation_alias="disableAdapters",
        serialization_alias="disableAdapters",
    )
    uses_guaranteed_capacity: bool | None = Field(
        default=None,
        validation_alias="usesGuaranteedCapacity",
        serialization_alias="usesGuaranteedCapacity",
    )
    chunked_prefill: bool | None = Field(
        default=None,
        validation_alias="chunkedPrefill",
        serialization_alias="chunkedPrefill",
    )
    speculation_disable_by_batch_size: int | None = Field(
        default=None,
        validation_alias="speculationDisableByBatchSize",
        serialization_alias="speculationDisableByBatchSize",
    )
    max_num_batched_tokens: int | None = Field(
        default=None,
        validation_alias="maxNumBatchedTokens",
        serialization_alias="maxNumBatchedTokens",
    )
    cache_model: bool | None = Field(
        default=None,
        validation_alias="cacheModel",
        serialization_alias="cacheModel",
    )
    merge_adapter: bool | None = Field(
        default=None,
        validation_alias="mergeAdapter",
        serialization_alias="mergeAdapter",
    )


class DeploymentConfig(UpdateDeploymentConfig):
    # Inherited from UpdateDeploymentConfig but now required.
    base_model: str = Field(
        ...,
        validation_alias="baseModel",
        serialization_alias="baseModel",
    )
    compute_spec: ServingComputeSpec | None = Field(
        validation_alias="computeSpec",
        serialization_alias="computeSpec",
        default=None,
    )
    quantization: str | None = Field(default=None)
    accelerator: str | None = Field(default=None)  # Deprecated


class ClassificationDeploymentConfig(DeploymentConfig):
    @model_validator(mode="after")
    def _ensure_required_custom_args(self):
        """
        Ensure that `custom_args` always contains:

            --task classify
        And also set defaults.

        Rules:
        1. If the user provides no custom_args → set exactly to the required args.
        2. If the user provides custom_args → remove any existing '--enforce-eager'
           and any '--task <value>' pair, then prepend our required args.
        3. Preserve the order of all other user-provided args.
        """
        required = ["--task", "classify"]
        defaults = ["--enforce-eager"]

        # Parse provded custom_args
        i = 0
        custom_args = list(self.custom_args or [])
        user_custom_args: list[str] = []
        while i < len(custom_args):
            arg = custom_args[i]

            if arg == "--enforce-eager":
                # Skip this since it's already in defaults
                i += 1
                continue
            elif arg == "--compile":
                # Only one of "--compile" or "--enforce_eager" should be set
                defaults.remove("--enforce_eager")

            if arg == "--task":
                # Skip this flag and its value (if provided),
                # since we enforce "--task classify"
                i += 2
                continue

            # All other args are preserved in their original order
            user_custom_args.append(arg)
            i += 1

        self.custom_args = required + defaults + user_custom_args
        return self


class AugmentationConfig(BaseModel):
    """Configuration for synthetic data generation tasks.

    # Attributes
    :param base_model: (str) The OpenAI model to prompt.
    :param num_samples_to_generate: (int) The number of synthetic examples to generate.
    :param num_seed_samples: (int) The number of seed samples to use for generating synthetic examples.
    :param task_context: (str) The user-provided task context for generating candidates.
    """

    base_model: str
    num_samples_to_generate: int = Field(default=1000)
    num_seed_samples: int | str = Field(default="all")
    augmentation_strategy: str = Field(default="mixture_of_agents")
    task_context: str = Field(default="")

    @field_validator("base_model")
    @classmethod
    def validate_base_model(cls, base_model) -> str:
        supoorted_base_models = {
            "gpt-4-turbo",
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-4o",
            "gpt-4o-2024-08-06",
            "gpt-4o-mini",
        }
        if base_model not in supoorted_base_models:
            raise ValueError(
                f"base_model must be one of {supoorted_base_models}.",
            )
        return base_model

    @field_validator("num_samples_to_generate")
    @classmethod
    def validate_num_samples_to_generate(cls, num_samples_to_generate) -> int:
        if num_samples_to_generate < 1:
            raise ValueError("num_samples_to_generate must be >= 1.")
        return num_samples_to_generate

    @field_validator("num_seed_samples")
    @classmethod
    def validate_num_seed_samples(cls, num_seed_samples):
        if isinstance(num_seed_samples, str) and num_seed_samples != "all":
            raise ValueError("num_seed_samples can only be an integer or the string 'all'.")
        elif isinstance(num_seed_samples, int) and num_seed_samples < 1:
            raise ValueError("num_seed_samples must be >= 1.")
        return num_seed_samples

    @field_validator("augmentation_strategy")
    @classmethod
    def validate_augmentation_strategy(cls, augmentation_strategy):
        if augmentation_strategy not in {"single_pass", "mixture_of_agents"}:
            raise ValueError("augmentation_strategy must be 'single_pass' or 'mixture_of_agents'.")
        return augmentation_strategy


class TrainingComputeSpec(BaseModel):
    region: str | None = Field(default=None)
    requests: TrainingComputeRequests | None = Field(default=None)


class TrainingComputeRequests(BaseModel):
    trainer: ComputeRequest
