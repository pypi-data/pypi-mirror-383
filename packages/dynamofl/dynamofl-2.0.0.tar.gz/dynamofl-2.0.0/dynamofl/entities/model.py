"""DynamoFL Model"""
import logging
from dataclasses import dataclass

from ..Helpers import URLUtils

logger = logging.getLogger(__name__)


@dataclass
class BaseModel:
    """Base Model Data class"""

    id: str
    key: str
    name: str
    config: object
    ui_url: str

    def __init__(
        self, id: str, key: str, name: str, config: object, api_host: str
    ):  # pylint: disable=redefined-builtin
        self.id = id
        self.key = key
        self.name = name
        self.config = config
        self.ui_url = URLUtils.get_model_ui_url(api_host=api_host, model_id=id)
        logger.info("Model UI URL: %s", self.ui_url)


@dataclass
class RemoteModelEntity(BaseModel):
    """Remote Model Data class"""

    type: str = "REMOTE"

    def __init__(
        self, id: str, key: str, name: str, config: object, api_host: str
    ):  # pylint: disable=redefined-builtin
        super().__init__(id=id, key=key, name=name, config=config, api_host=api_host)
