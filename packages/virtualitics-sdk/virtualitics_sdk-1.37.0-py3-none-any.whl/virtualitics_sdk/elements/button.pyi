from _typeshed import Incomplete
from enum import Enum
from virtualitics_sdk import drilldown_callback_type as drilldown_callback_type
from virtualitics_sdk.elements.element import Element as Element, ElementType as ElementType
from virtualitics_sdk.icons import ALL_ICONS as ALL_ICONS

class ButtonStyle(Enum):
    SECONDARY: str

class ButtonType(Enum):
    STANDARD: str
    ASSET_DOWNLOAD: str
    TRIGGER_FLOW: str
    DRILLDOWN: str

class Button(Element):
    on_click: Incomplete
    button_type: Incomplete
    def __init__(self, *, title: str, confirmation_text: str | None = None, label: str | None = None, icon: str | None = None, on_click: drilldown_callback_type | None = None, button_type: ButtonType | None = ..., style: ButtonStyle | None = ..., horizontal_position=None, vertical_position=None, tooltip: str | None = None, open_new_tab: bool | None = False, **kwargs) -> None: ...
    @staticmethod
    def get_asset_download_params(asset, label, extension, mime_type): ...
    def to_json(self) -> dict: ...
