from typing import Literal

from pydantic import Field

from ._base_config import BasePropertyConfig
from ....models.primitives import EmptyObject
from ....properties.base_properties._base_property import NotionPropertyType


class UrlPropertyConfig(BasePropertyConfig[Literal[NotionPropertyType.URL]]):
    """Notionのurlプロパティ設定"""

    type: Literal[NotionPropertyType.URL] = Field(
        NotionPropertyType.URL, description="プロパティタイプ"
    )
    url: EmptyObject = Field(
        default_factory=EmptyObject, description="url設定"
    )
