from abc import ABC
from typing import List

from peewee import DoesNotExist

from entity.BaseModel import Character, Character2db


class CharacterMapperInterface(ABC):

    def create_character(self, character: Character) -> bool:
        raise NotImplementedError

    def get_character_by_id(self, character_id) -> Character:
        raise NotImplementedError

    def get_characters(self) -> List[Character]:
        raise NotImplementedError

    def update_character_by_id(self, character_id, character: Character) -> bool:
        raise NotImplementedError

    def delete_character_by_id(self, character_id) -> bool:
        raise NotImplementedError


class CharacterMapper(CharacterMapperInterface):
    """
    负责在 Character 类实例和数据库模型 Character2db 之间进行转换和操作。
    """
    def create_character(self, character: Character):
        """
        创建一个新的角色记录。

        Args:
            character: 包含角色信息的 Character 对象。

        Returns:
            如果创建成功则返回 True，否则返回 False。
        """
        try:
            # 使用 Character 对象的数据创建数据库记录
            Character2db.create(
                name=character.name,
                prompt=character.prompt
            )
            return True
        except Exception as e:
            print(f"创建角色失败: {e}")
            return False

    def get_character_by_id(self, character_id):
        """
        根据 ID 获取单个角色。

        Args:
            character_id: 角色 ID。

        Returns:
            如果找到，则返回一个 Character 对象；否则返回 None。
        """
        try:
            # 在数据库中查找记录
            character_db = Character2db.get(Character2db.id == character_id)
            # 将数据库记录转换为 Character 对象
            return Character(
                character_id=character_db.id,
                name=character_db.name,
                prompt=character_db.prompt,
                is_visible=character_db.is_visible,
            )
        except DoesNotExist:
            print(f"角色 ID {character_id} 不存在。")
            return None
        except Exception as e:
            print(f"获取角色失败: {e}")
            return None

    def get_characters(self):
        """
        获取所有角色记录。

        Returns:
            一个包含所有 Character 对象的列表。
        """
        characters_list = []
        # 查询所有记录
        for character_db in Character2db.select():
            # 将每条记录转换为 Character 对象并添加到列表中
            characters_list.append(
                Character(
                    character_id=character_db.id,
                    name=character_db.name,
                    prompt=character_db.prompt,
                    is_visible=character_db.is_visible,
                )
            )
        return characters_list

    def update_character_by_id(self, character_id, character: Character):
        """
        根据 ID 更新角色的信息。

        Args:
            character_id: 要更新的角色的 ID。
            character: 包含新信息的 Character 对象。

        Returns:
            如果更新成功则返回 True，否则返回 False。
        """
        try:
            # 查找要更新的记录
            character_db = Character2db.get(Character2db.id == character_id)
            # 更新字段
            character_db.name = character.name
            character_db.prompt = character.prompt
            character_db.is_visible = character.is_visible
            # 保存更改
            character_db.save()
            return True
        except DoesNotExist:
            print(f"更新失败：角色 ID {character_id} 不存在。")
            return False
        except Exception as e:
            print(f"更新角色失败: {e}")
            return False

    def delete_character_by_id(self, character_id):
        """
        根据 ID 删除角色记录。

        Args:
            character_id: 要删除的角色的 ID。

        Returns:
            如果删除成功则返回 True，否则返回 False。
        """
        try:
            char = Character2db.get_or_none(Character2db.id == character_id)
            if char:
                char.delete_instance(recursive=True)  # recursive=True 也会删除反向依赖对象
                return True
            return False
        except Exception as e:
            print(f"删除角色失败: {e}")
            return False


if __name__ == '__main__':
    mapper = CharacterMapper()
