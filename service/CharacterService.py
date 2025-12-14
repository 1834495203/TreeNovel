from abc import ABC
from typing import List

from entity.BaseModel import Character
from mapper.CharacterMapper import CharacterMapper, CharacterMapperInterface
from mapper.CharacterSceneMapper import CharacterSceneMapper, CharacterSceneMapperInterface


class CharacterServiceInterface(ABC):

    def get_character_by_id(self, character_id: int) -> Character:
        """
        根据角色ID获取角色信息

        Args:
            character_id: 角色ID

        Return:
            角色信息
        """
        raise NotImplementedError

    def create_character(self, character: Character) -> Character:
        """
        创建新角色

        Args:
            character: 角色信息

        Return:
            创建的角色
        """
        raise NotImplementedError

    def update_character(self, character_id: int, character: Character) -> Character:
        """
        更新角色信息

        Args:
            character_id: 角色ID
            character: 新角色信息

        Return:
            更新后的角色
        """
        raise NotImplementedError

    def delete_character(self, character_id: int) -> bool:
        """
        删除角色

        Args:
            character_id: 角色ID

        Return:
            是否删除成功
        """
        raise NotImplementedError

    def get_all_characters(self) -> List[Character]:
        """
        获取所有角色

        Return:
            角色列表
        """
        raise NotImplementedError

    def disconnect_character_from_scene(self, character_id: int, scene_id: str) -> bool:
        """
        删除角色与场景的关联

        Args:
            character_id: 角色ID
            scene_id: 场景ID

        Return:
            是否删除成功
        """
        raise NotImplementedError


class CharacterService(CharacterServiceInterface):
    """
    角色相关的service
    """

    def __init__(self, character_mapper: CharacterMapperInterface,
                 character_scene_mapper: CharacterSceneMapperInterface = None):
        self._character_mapper = character_mapper
        self._character_scene_mapper = character_scene_mapper or CharacterSceneMapper()

    def get_character_by_id(self, character_id: int) -> Character:
        """
        根据角色ID获取角色信息

        Args:
            character_id: 角色ID

        Return:
            角色信息
        """
        character_db = self._character_mapper.get_character_by_id(character_id)
        return Character(
            character_id=character_id,
            name=character_db.name,
            prompt=character_db.prompt,
            is_visible=character_db.is_visible,
        )

    def create_character(self, character: Character) -> Character:
        """
        创建新角色

        Args:
            character: 角色信息

        Return:
            创建的角色
        """
        success = self._character_mapper.create_character(character)

        if success:
            # 获取最新创建的角色（假设是按ID倒序，最新创建的ID最大）
            all_characters = self._character_mapper.get_characters()
            if all_characters:
                # 返回最新创建的角色
                return max(all_characters, key=lambda c: c.character_id)
        else:
            raise Exception("创建角色失败")

    def update_character(self, character_id: int, character: Character) -> Character:
        """
        更新角色信息

        Args:
            character_id: 角色ID
            character: 新角色信息

        Return:
            更新后的角色
        """
        success = self._character_mapper.update_character_by_id(character_id, character)

        if success:
            # 获取更新后的角色信息
            updated_character = self._character_mapper.get_character_by_id(character_id)
            if updated_character is None:
                raise Exception("更新后获取角色信息失败")
            return updated_character
        else:
            raise Exception(f"更新角色 {character_id} 失败")

    def delete_character(self, character_id: int) -> bool:
        """
        删除角色

        Args:
            character_id: 角色ID

        Return:
            是否删除成功
        """
        return self._character_mapper.delete_character_by_id(character_id)

    def get_all_characters(self) -> List[Character]:
        """
        获取所有角色

        Return:
            角色列表
        """
        return self._character_mapper.get_characters()

    def disconnect_character_from_scene(self, character_id: int, scene_id: str) -> bool:
        """
        删除角色与场景的关联

        Args:
            character_id: 角色ID
            scene_id: 场景ID

        Return:
            是否删除成功
        """
        return self._character_scene_mapper.disconnect_character_from_scene(character_id, scene_id)


if __name__ == '__main__':
    character_service = CharacterService(CharacterMapper())
