import os
from typing import Optional
from openai import OpenAI

from .utils import get_logger

logger = get_logger(__name__)


class EndPoint:
    """
    A class that represents an endpoint to interact with the OpenAI client,
    allowing for the configuration of organization and project IDs.

    Attributes:
        __organization__ (Optional[str]): The organization ID for the OpenAI client.
        __project_id__ (Optional[str]): The project ID for the OpenAI client.

    Methods:
        __init__(organization: Optional[str], project_id: Optional[str]):
            Initializes the EndPoint instance with optional organization and project IDs.
        set_organization(organization: Optional[str]):
            Sets the organization ID at the class level.
        set_project_id(project_id: Optional[str]):
            Sets the project ID at the class level.
        get_client(organization: Optional[str], project_id: Optional[str]) -> OpenAI:
            Returns an instance of the OpenAI client using the provided or default organization and project IDs.
        reset_client():
            Resets the OpenAI client instance using the current configuration.
    """

    __organization__: Optional[str] = None
    __project_id__: Optional[str] = None

    def __init__(
        self, organization: Optional[str] = None, project_id: Optional[str] = None
    ):
        """
        Initializes the EndPoint instance.

        Args:
            organization (Optional[str]): The organization ID. Defaults to None.
            project_id (Optional[str]): The project ID. Defaults to None.
        """
        EndPoint.verify_openai_api_key()
        if organization is not None:
            self.__organization__ = organization
        if project_id is not None:
            self.__project_id__ = project_id
        self._client = self.get_client()

    @classmethod
    def verify_openai_api_key(cls) -> None:
        """
        Verify that the OpenAI API key is set and non-empty in the environment variables.

        This function checks if the environment variable `OPENAI_API_KEY` exists and ensures
        that it is not empty. If the environment variable is not set or is empty, it raises
        a `ValueError` with an appropriate message.

        Raises:
            ValueError: If `OPENAI_API_KEY` is not set or is an empty string.
        """
        # verify $OPENAI_API_KEY is set
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("Please set the OPENAI_API_KEY environment variable")

        # verify $OPENAI_API_KEY is not empty
        if os.environ["OPENAI_API_KEY"] == "" or os.environ["OPENAI_API_KEY"] is None:
            raise ValueError("OPENAI_API_KEY is empty")

    @classmethod
    def set_organization(cls, organization: Optional[str]):
        """
        Sets the organization ID for the class.

        Args:
            organization (Optional[str]): The organization ID to be set. Must be a string or None.

        Raises:
            ValueError: If the organization is not a string or None.
        """
        if type(organization) != str and organization is not None:
            raise ValueError("organization must be a string or None")
        cls.__organization__ = organization

    @classmethod
    def set_project_id(cls, project_id: Optional[str]):
        """
        Sets the project ID for the class.

        Args:
            project_id (Optional[str]): The project ID to be set. Must be a string or None.

        Raises:
            ValueError: If the project_id is not a string or None.
        """
        if type(project_id) != str and project_id is not None:
            raise ValueError("project_id must be a string or None")
        cls.__project_id__ = project_id

    def get_client(
        self, organization: Optional[str] = None, project_id: Optional[str] = None
    ):
        """
        Creates and returns an OpenAI client using the provided or default organization and project IDs.

        Args:
            organization (Optional[str]): The organization ID to be used. Defaults to the class-level organization.
            project_id (Optional[str]): The project ID to be used. Defaults to the class-level project ID.

        Returns:
            OpenAI: An instance of the OpenAI client.
        """
        if organization is None:
            organization = self.__organization__
        if project_id is None:
            project_id = self.__project_id__
        logger.info(
            f"Creating OpenAI client with organization {organization} and project {project_id}"
        )
        return OpenAI(organization=organization, project=project_id)

    def reset_client(self):
        """
        Resets the OpenAI client instance using the current organization and project IDs.
        """
        self._client = self.get_client()
