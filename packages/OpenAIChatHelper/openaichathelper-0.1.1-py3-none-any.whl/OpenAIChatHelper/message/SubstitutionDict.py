class SubstitutionDict(dict):
    """
    A dictionary that only allows string keys and values.
    """

    def __setitem__(self, key: str, value: str) -> None:
        """
        Set a string key-value pair.

        Args:
            key (str): The dictionary key.
            value (str): The associated value.

        Raises:
            ValueError: If `key` or `value` is not a string.
        """
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> str:
        """
        Get the value for a string key.

        Args:
            key (str): The dictionary key.

        Raises:
            ValueError: If `key` is not a string.

        Returns:
            str: The associated value.
        """
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        return super().__getitem__(key)
