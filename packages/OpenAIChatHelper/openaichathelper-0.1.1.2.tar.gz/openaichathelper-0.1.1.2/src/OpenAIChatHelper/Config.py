from typing import Optional
from .EndPoint import EndPoint
from .utils import get_logger

logger = get_logger(__name__)


def set_default_authorization(
    organization: Optional[str] = None, project_id: Optional[str] = None
) -> None:
    """
    Sets the default authorization details for the EndPoint by configuring the
    organization and project ID. This method updates the default organization
    and project ID settings used for making API requests.

    Args:
        organization (Optional[str]): The organization ID to set. If None,
                                      the current organization remains unchanged.
        project_id (Optional[str]): The project ID to set. If None,
                                    the current project remains unchanged.

    Returns:
        None
    """
    EndPoint.set_organization(organization)
    EndPoint.set_project_id(project_id)
    logger.info(f"Set organization to {organization}")
    logger.info(f"Set project_id to {project_id}")
