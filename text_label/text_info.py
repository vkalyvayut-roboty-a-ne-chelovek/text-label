from dataclasses import dataclass
from typing import Optional


@dataclass
class TextInfo:
    text: str
    category_id: Optional[int] = None
