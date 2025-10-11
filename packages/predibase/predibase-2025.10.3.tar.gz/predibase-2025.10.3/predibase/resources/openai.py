from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from openai import ChatCompletion, OpenAI
from openai.types import Completion, CreateEmbeddingResponse

from predibase.pql.api import Session

if TYPE_CHECKING:
    from predibase.resources.deployment import Deployment


def openai_compatible_endpoint(session: Session, deployment_ref: Union[str, "Deployment"]) -> str:
    # Check not isinstance(deployment_ref, str) instead of
    #  isinstance(deployment_ref, Deployment) to avoid import error.
    if not isinstance(deployment_ref, str):
        deployment_ref = deployment_ref.name

    return f"https://{session.serving_http_endpoint}/{session.tenant}/deployments/v2/llms/" f"{deployment_ref}/v1"


def create_openai_client(url, session: Session):
    return


def build_extra_body(extra_body: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """Build the extra_body parameter for an OpenAI client request.

    This allows users to pass in extra body parameters to the OpenAI client request
    with additional parameters that have been exposed in the create methods.

    Args:
        extra_body: Existing extra body to merge with the new kwargs.
        **kwargs: The keyword arguments to add to the extra body.

    Returns:
        The merged extra body dictionary.
    """
    # Initialize the extra body dictionary or create a copy of the user-provided dictionary.
    if extra_body is None:
        extra_body = {}
    else:
        extra_body = extra_body.copy()

    # Merge the new kwargs into the extra body.
    for key, value in kwargs.items():
        if value is not None:
            extra_body[key] = value
    return extra_body


class OpenAIBase:
    def __init__(self, client):
        self._pb_client = client
        self._client = None
        self.model = None

    def init_client(self, model: str):
        if self.model != model:
            deployment = self._pb_client.deployments.get(model)
            openai_url = openai_compatible_endpoint(self._pb_client._session, deployment)
            self._client = OpenAI(api_key=self._pb_client._session.token, base_url=openai_url)
            self.model = model


class OpenAIChatCompletion(OpenAIBase):
    def __init__(self, client: OpenAI):
        super().__init__(client)

    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        adapter_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        hugging_face_api_key: Optional[str] = None,
        **kwargs,
    ) -> ChatCompletion:
        """
        Create a chat completion for the given model.

        Args:
            model: The deployment to prompt.
            messages: The messages to send to the deployment.
            adapter_id: The adapter to prompt.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for the completion.
            hugging_face_api_key: The API key to use for the completion, allows access to private adapters.
            **kwargs: Enables users to pass the full range of parameters supported by the OpenAI client.

        Returns:
            The chat completion response.
        """
        self.init_client(model)
        extra_body = kwargs.pop("extra_body", None)
        extra_body = build_extra_body(extra_body=extra_body, api_token=hugging_face_api_key)

        return self._client.chat.completions.create(
            model=adapter_id or "",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body=extra_body,
            **kwargs,
        )


class OpenAICompletion(OpenAIBase):
    def __init__(self, client):
        super().__init__(client)

    def create(
        self,
        model: str,
        prompt: str,
        adapter_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        hugging_face_api_key: Optional[str] = None,
        **kwargs,
    ) -> Completion:
        """
        Create a completion for the given model.

        Args:
            model: The deployment to prompt.
            prompt: The prompt to send to the deployment.
            adapter_id: The adapter to prompt.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for the completion.
            hugging_face_api_key: The API key to use for the completion, allows access to private adapters.
            **kwargs: Enables users to pass the full range of parameters supported by the OpenAI client.

        Returns:
            The completion response.
        """
        self.init_client(model)
        extra_body = kwargs.pop("extra_body", None)
        extra_body = build_extra_body(extra_body=extra_body, api_token=hugging_face_api_key)

        return self._client.completions.create(
            model=adapter_id or "",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            extra_body=extra_body,
            **kwargs,
        )


class OpenAIEmbeddings(OpenAIBase):
    def __init__(self, client):
        super().__init__(client)

    def create(
        self,
        model: str,
        input: str,
        adapter_id: Optional[str] = None,
        hugging_face_api_key: Optional[str] = None,
        **kwargs,
    ) -> CreateEmbeddingResponse:
        """
        Create embeddings for the given model.

        Args:
            model: The deployment to create embeddings from.
            input: The input to create embeddings from.
            adapter_id: The adapter to create embeddings from.
            hugging_face_api_key: The API key to use for the embeddings, allows access to private adapters.
            **kwargs: Enables users to pass the full range of parameters supported by the OpenAI client.

        Returns:
            The embedding response.
        """
        self.init_client(model)
        extra_body = kwargs.pop("extra_body", None)
        extra_body = build_extra_body(extra_body=extra_body, api_token=hugging_face_api_key)

        return self._client.embeddings.create(
            model=adapter_id or "",
            input=input,
            extra_body=extra_body,
            **kwargs,
        )


class OpenAIChat:
    def __init__(self, client):
        self.completion = OpenAIChatCompletion(client)
