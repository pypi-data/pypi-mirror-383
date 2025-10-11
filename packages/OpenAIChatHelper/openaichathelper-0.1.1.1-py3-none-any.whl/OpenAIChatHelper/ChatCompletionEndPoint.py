from typing import Optional, List, Tuple
import random
import asyncio
from openai.types.chat import ChatCompletion
from .EndPoint import EndPoint
from .message.Message import Message, get_assistant_message_from_response
from .message.MessageList import MessageList
from .message.SubstitutionDict import SubstitutionDict
from .utils import get_logger

logger = get_logger(__name__)


class ChatCompletionEndPoint(EndPoint):
    """
    A class to handle chat completions using a specified model.

    Attributes:
        _default_model (str): The default model to use for chat completions.

    Methods:
        completions(messages, substitution_dict=None, model=None, **kwargs):
            Generate chat completions using the provided messages and optional substitutions.
    """

    def __init__(
        self,
        default_model: str,
        organization: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize the ChatCompletionEndPoint instance with a default model, organization, and project ID.

        Args:
            default_model (str): The default model to use for chat completions.
            organization (Optional[str]): The organization identifier (optional).
            project_id (Optional[str]): The project ID (optional).
        """
        super().__init__(organization, project_id)
        self._default_model = default_model

    async def completions(
        self,
        message_list: MessageList,
        substitution_dict: Optional[SubstitutionDict] = None,
        model: Optional[str] = None,
        store: bool = False,
        retry: int = 5,
        **kwargs,
    ) -> Tuple[List[Message], ChatCompletion]:
        """
        Generate chat completions using the provided message_list and optional substitutions. The completions are generated without streaming.

        Args:
            message_list (MessageList): The list of messages to use for generating completions.
            substitution_dict (Optional[SubstitutionDict]): A dictionary for substituting variables in messages (optional).
            model (Optional[str]): The model to use for generating completions. Defaults to the instance's default model if not provided.
            store (bool): Whether to store the chat completion in the database. Defaults to False.
            retry (int): The number of retry attempts for the API call. Defaults to 5.
            **kwargs: Additional arguments to pass to the chat completions API.

        Returns:
            Message: The generated chat completion.
        """
        if "stream" in kwargs:
            logger.warning(
                "The 'stream' parameter is not supported in the 'completions' method"
            )
            del kwargs["stream"]
        if model is None:
            model = self._default_model

        async def _call():
            # Offload blocking SDK call to a thread
            return await asyncio.to_thread(
                self._client.chat.completions.create,
                model=model,
                messages=message_list.to_dict(substitution_dict),
                store=store,
                **kwargs,
            )

        last_exc = None

        for attempt in range(1, retry + 1):
            try:
                res: ChatCompletion = await _call()
                choices = getattr(res, "choices", None) or []
                if not choices:
                    raise RuntimeError("No choices returned from completion API.")
                responses = [
                    get_assistant_message_from_response(c.message) for c in choices
                ]
                return responses, res
            except Exception as e:
                last_exc = e
                # decide if error is retryable; if not, raise immediately
                # if not is_retryable(e): raise
                if attempt == retry:
                    raise
                # exponential backoff with jitter
                base = 2 ** (attempt - 1)
                delay = base + random.uniform(-0.2 * base, 0.2 * base)
                await asyncio.sleep(max(0.0, delay))
            raise last_exc
