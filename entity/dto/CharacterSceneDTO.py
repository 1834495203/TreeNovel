from dataclasses import dataclass
from typing import Optional

from entity.BaseModel import CharacterSceneRecord, Character


@dataclass
class CharacterSceneDto(CharacterSceneRecord):
    character: Optional[Character] = None
