from typing import Dict, Optional, Literal, List
from .SubstitutionDict import SubstitutionDict
from ..utils import remove_markdown, split_ordered_list


class Content:
    """Abstract base class for different types of content."""

    def __init__(self, content_type: str = "undefined"):
        self._content_type = content_type

    @property
    def content_type(self) -> str:
        return self._content_type

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = SubstitutionDict()
    ) -> Dict:
        """
        Convert the content to a dictionary format.

        Args:
            substitution_dict (Optional[SubstitutionDict]): A dictionary for substituting values
            within the content. Defaults to an empty dictionary.

        Returns:
            Dict: The dictionary representation of the content.
        """
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError


class TextContent(Content):
    """Represents textual content."""

    def __init__(self, text: str):
        """
        Initialize TextContent.

        Args:
            text (str): The text content.

        Raises:
            ValueError: If `text` is not a string.
        """
        super().__init__("text")
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = SubstitutionDict()
    ) -> Dict:
        return {"type": "text", "text": self._text.format_map(substitution_dict)}

    def __repr__(self):
        return f"\033[36mText:\033[0m {self._text}".replace("\n", "\n" + " " * 6)

    def split_ordered_list(
        self,
        remove_markdown_option: List = [
            "heading",
            "emphasis",
            "strong",
            "horizontal_rule",
            "block_quote",
        ],
        **kwargs,
    ) -> List[str]:
        """
        Split the text content into an ordered list.

        Args:
            remove_markdown (List): Whether to remove markdown formatting from the text content.
            **kwargs: Additional arguments to pass to the `split_ordered_list` function.

        Returns:
            List[str]: The ordered list of text items.
        """
        return split_ordered_list(self._text, remove_markdown_option, **kwargs)

    def remove_markdown(self, **kwargs) -> str:
        """
        Remove markdown formatting from the text content.

        Args:
            **kwargs: Additional arguments to pass to the `remove_markdown` function.

        Returns:
            str: The text content without markdown.
        """
        return remove_markdown(self._text, **kwargs)


class ImageContent(Content):
    """Represents image content with a URL and optional detail level."""

    def __init__(
        self,
        image_url: str,
        image_details: Optional[Literal["low", "high", "auto"]] = None,
    ):
        """
        Initialize ImageContent.

        Args:
            image_url (str): The URL of the image.
            image_details (Optional[Literal["low", "high", "auto"]]): Detail level of the image.

        Raises:
            ValueError: If `image_url` is not a string or `image_details` is invalid.
        """
        super().__init__("image")
        if not isinstance(image_url, str):
            raise ValueError("Image URL must be a string")
        if image_details not in {None, "low", "high", "auto"}:
            raise ValueError(
                "Invalid image details; if provided, must be 'low', 'high', or 'auto'"
            )
        self._image_url = image_url
        self._image_details = image_details

    @property
    def image_url(self) -> str:
        return self._image_url

    @property
    def image_details(self) -> Optional[Literal["low", "high", "auto"]]:
        return self._image_details

    def to_dict(self, _: Optional[SubstitutionDict] = SubstitutionDict()) -> Dict:
        image_data = {"url": self._image_url}
        if self._image_details:
            image_data["detail"] = self._image_details
        return {"type": "image_url", "image_url": image_data}

    def __repr__(self):
        detail = f" ({self._image_details})" if self._image_details else ""
        return f"\033[36mImage{detail}:\033[0m {self._image_url[:15]}..."


class AudioContent(Content):
    """Represents audio content with data and format."""

    def __init__(
        self,
        audio_data: str,
        audio_format: Literal["mp3", "wav"],
    ):
        """
        Initialize AudioContent.

        Args:
            audio_data (str): The audio data.
            audio_format (Literal["mp3", "wav"]): The format of the audio.

        Raises:
            ValueError: If `audio_data` is not a string or `audio_format` is invalid.
        """
        super().__init__("audio")
        if not isinstance(audio_data, str):
            raise ValueError("Audio data must be a string")
        if audio_format not in {"mp3", "wav"}:
            raise ValueError("Invalid audio format; must be 'mp3' or 'wav'")
        self._audio_data = audio_data
        self._audio_format = audio_format

    @property
    def audio_data(self) -> str:
        return self._audio_data

    @property
    def audio_format(self) -> Literal["mp3", "wav"]:
        return self._audio_format

    def to_dict(self, _: Optional[SubstitutionDict] = SubstitutionDict()) -> Dict:
        return {
            "type": "input_audio",
            "input_audio": {"data": self._audio_data, "format": self._audio_format},
        }

    def __repr__(self):
        return (
            f"\033[36mAudio ({self._audio_format}):\033[0m {self._audio_data[:15]}..."
        )


class RefusalContent(Content):
    """Represents refusal content."""

    def __init__(self, refusal: str):
        """
        Initialize RefusalContent.

        Args:
            refusal (str): The refusal message.

        Raises:
            ValueError: If `refusal` is not a string.
        """
        super().__init__("refusal")
        if not isinstance(refusal, str):
            raise ValueError("Refusal must be a string")
        self._refusal = refusal

    @property
    def refusal(self) -> str:
        return self._refusal

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = SubstitutionDict()
    ) -> Dict:
        return {
            "type": "refusal",
            "refusal": self._refusal.format_map(substitution_dict),
        }

    def __repr__(self):
        return f"\033[36mRefusal:\033[0m {self._refusal}".replace("\n", "\n" + " " * 9)
