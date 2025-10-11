from typing import Optional, Dict, List

from .Message import Message
from .SubstitutionDict import SubstitutionDict


class MessageList:
    """A list of messages in a conversation."""

    def __init__(self):
        """Initialize an empty MessageList."""
        self._messages = []
        self._system_message = None

    def __len__(self):
        """Return the number of messages in the list."""
        return len(self._messages)

    def __getitem__(self, index: int) -> Message:
        """Return the message at the specified index."""
        return self._messages[index]

    def add_message(
        self,
        message: Message,
    ) -> None:
        """Add a message to the message list.

        Args:
            message (Message): The message to add.

        Raises:
            ValueError: If the message role is not 'user' or 'assistant'.
        """
        if not isinstance(message, Message):
            raise ValueError("message must be a Message object")
        self._messages.append(message)

    def modify_message(self, index: int, message: Message) -> None:
        """Modify a message at a specific index.

        Args:
            index (int): The index of the message to modify.
            message (Message): The new message to replace the existing one.
        """
        if not isinstance(message, Message):
            raise ValueError("message must be a Message object")
        self._messages[index] = message

    def pop_message(self) -> Message:
        """Remove and return the last message from the message list.

        Returns:
            Message: The last message in the message list.

        Raises:
            ValueError: If there are no messages to pop.
        """
        if not self._messages:
            raise ValueError("No message to pop")
        return self._messages.pop()

    def pop_messages(self, repeat: int) -> List[Message]:
        """Remove and return the last `repeat` messages from the message list.

        Args:
            repeat (int): The number of messages to pop.

        Returns:
            List[Message]: The last `repeat` messages in the message list.

        Raises:
            ValueError: If there are not enough messages to pop.
        """
        if len(self._messages) < repeat:
            raise ValueError("Not enough messages to pop")
        return [self._messages.pop() for _ in range(repeat)]

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = None
    ) -> List[Dict]:
        """Convert the message list to a dictionary.

        Args:
            substitution_dict (Optional[SubstitutionDict], optional): The substitution dictionary for the message content. Defaults to None.

        Returns:
            List[Dict]: The message list as a list of dictionaries.
        """
        return [message.to_dict(substitution_dict) for message in self._messages]

    def __repr__(self):
        """Return a string representation of the message list."""
        messages = [f"{message}" for message in self._messages]
        return "\n".join(messages)
