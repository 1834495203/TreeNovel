from entity.BaseModel import CharacterSceneRecord, CharacterScene
from typing import List, Optional
from abc import ABC


class CharacterSceneMapperInterface(ABC):

    def get_character_scene_by_scene_id(self, scene_id: str) -> List[CharacterSceneRecord]:
        """
        根据场景ID获取所有关联的角色场景记录。

        Args:
            scene_id: 场景的唯一标识符

        Returns:
            CharacterSceneRecord对象列表，包含该场景下所有角色的关联信息
        """
        raise NotImplementedError

    def connect_character_2_scene(self, character_scene: CharacterSceneRecord) -> bool:
        """
        创建角色与情景的关联

        Args:
            character_scene: 角色id
            scene_id: 场景id

        Returns:
            bool
        """
        raise NotImplementedError

    def is_character_visible(self, character_id: int, scene_id: str) -> bool:
        """
        查询角色在场景下是否可见

        Args:
            character_id: 角色id
            scene_id: 情景id

        Returns:
            bool
        """
        raise NotImplementedError

    def is_character_in_scene(self, character_id: int, scene_id: str) -> bool:
        """
        查询角色在场景下是否存在

        Args:
            character_id: 角色id
            scene_id: 情景id

        Returns:
            bool
        """
        raise NotImplementedError

    def is_character_in_any_scenes(self, character_id: int, scene_ids: List[str]) -> bool:
        """
        批量判断：角色是否在给定的多个场景中的任意一个里出现

        Args:
            character_id: 角色ID
            scene_ids: 场景ID列表

        Returns:
            bool: True 表示角色至少在一个场景中出现
        """
        raise NotImplementedError

    def character_first_in_any_scenes(self, character_id: int, scene_ids: List[str]) -> Optional[CharacterSceneRecord]:
        """
        用于返回在一个情景链中角色最新出现的情景，scene_ids必须从最新的情景开始排列

        Args:
            character_id: 角色ID
            scene_ids: 场景ID列表，必须从最新开始排列

        Returns:
            CharacterSceneRecord: 返回
        """
        raise NotImplementedError

    def disconnect_character_from_scene(self, character_id: int, scene_id: str) -> bool:
        """
        删除角色与场景的关联

        Args:
            character_id: 角色ID
            scene_id: 场景ID

        Returns:
            bool: 是否删除成功
        """
        raise NotImplementedError

    def disconnect_all_characters_from_scene(self, scene_id: str) -> bool:
        """
        批量删除场景下所有角色关联记录

        Args:
            scene_id: 场景ID

        Returns:
            bool: 是否删除成功
        """
        raise NotImplementedError


class CharacterSceneMapper(CharacterSceneMapperInterface):

    def get_character_scene_by_scene_id(self, scene_id: str, include_invisible: bool = False) -> List[CharacterSceneRecord]:
        try:
            character_scene_records = []

            # 查询所有关联的角色场景记录
            query = CharacterScene.select().where(CharacterScene.sid == scene_id)
            if not include_invisible:
                query = query.where(CharacterScene.is_visible == True)
            
            query_results = query

            for record in query_results:
                character_scene_record = CharacterSceneRecord(
                    character_scene_id=record.id,
                    character_id=record.character_id,
                    sid=record.sid,
                    sort_order=record.sort_order,
                    is_visible=record.is_visible,
                    parent_id=record.parent_id.id if record.parent_id else None
                )
                character_scene_records.append(character_scene_record)

            # 按sort_order排序
            character_scene_records.sort(key=lambda x: x.sort_order)

            return character_scene_records

        except Exception as e:
            print(f"根据场景ID获取角色场景记录失败: {e}")
            return []

    def connect_character_2_scene(self, character_scene: CharacterSceneRecord) -> bool:
        try:
            CharacterScene.create(
                character_id=character_scene.character_id,
                sid=character_scene.sid,
                sort_order=character_scene.sort_order,
                is_visible=character_scene.is_visible,
            )
            return True
        except Exception as e:
            print(f"连接角色与情景失败: {e}")
            return False

    def is_character_visible(self, character_id: int, scene_id: str) -> bool:
        """
        查询角色在场景下是否可见
        注意：此方法已废弃，角色可见性应该通过Character.is_visible来判断
        为了向后兼容，此方法现在只检查角色是否在场景中

        Args:
            character_id: 角色id
            scene_id: 情景id

        Returns:
            bool: 角色是否在场景中
        """
        return self.is_character_in_scene(character_id, scene_id)

    def is_character_in_scene(self, character_id: int, scene_id: str) -> bool:
        return (CharacterScene.select()
                .where(CharacterScene.sid == scene_id)
                .where(CharacterScene.character_id == character_id).exists())

    def is_character_in_any_scenes(self, character_id: int, scene_ids: List[str]) -> bool:
        if not scene_ids:
            return False

        return (CharacterScene.select()
                .where(CharacterScene.character_id == character_id)
                .where(CharacterScene.sid << scene_ids)
                .limit(1)
                .exists())

    def character_first_in_any_scenes(self, character_id: int, scene_ids: List[str], include_invisible: bool = False) -> Optional[CharacterSceneRecord]:
        """
        用于返回在一个情景链中角色最新出现的情景，scene_ids必须从最新的情景开始排列

        Args:
            character_id: 角色ID
            scene_ids: 场景ID列表，必须从最新开始排列
            include_invisible: 是否包含不可见角色

        Returns:
            CharacterSceneRecord: 返回角色在场景链中最新出现的场景记录
        """
        if not scene_ids:
            return None

        try:
            # 构建场景优先级映射（从最新开始，优先级最高）
            scene_priority = {scene_id: index for index, scene_id in enumerate(scene_ids)}
            
            # 查询角色在所有指定场景中的所有记录
            query = (CharacterScene.select()
                    .where(CharacterScene.character_id == character_id)
                    .where(CharacterScene.sid << scene_ids))
            
            if not include_invisible:
                query = query.where(CharacterScene.is_visible == True)
            
            query_results = query
            
            # 将查询结果转换为列表并按场景优先级排序（最新的场景优先级最高）
            def get_priority(record):
                return scene_priority.get(record.sid, len(scene_ids))
            
            sorted_results = sorted(query_results, key=get_priority)
            
            # 获取优先级最高的记录（第一个）
            if sorted_results:
                record = sorted_results[0]
                return CharacterSceneRecord(
                    character_scene_id=record.id,
                    character_id=record.character_id,
                    sid=record.sid,
                    sort_order=record.sort_order,
                    is_visible=record.is_visible,
                    parent_id=record.parent_id.id if record.parent_id else None
                )
            
            return None

        except Exception as e:
            print(f"获取角色在场景链中最新出现记录失败: {e}")
            return None

    def disconnect_character_from_scene(self, character_id: int, scene_id: str) -> bool:
        """
        删除角色与场景的关联

        Args:
            character_id: 角色ID
            scene_id: 场景ID

        Returns:
            bool: 是否删除成功
        """
        try:
            deleted_count = (CharacterScene.delete()
                           .where(CharacterScene.character_id == character_id)
                           .where(CharacterScene.sid == scene_id)
                           .execute())
            return deleted_count > 0
        except Exception as e:
            print(f"删除角色与场景关联失败: {e}")
            return False

    def disconnect_all_characters_from_scene(self, scene_id: str) -> bool:
        """
        批量删除场景下所有角色关联记录

        Args:
            scene_id: 场景ID

        Returns:
            bool: 是否删除成功
        """
        try:
            deleted_count = (CharacterScene.delete()
                           .where(CharacterScene.sid == scene_id)
                           .execute())
            return deleted_count >= 0  # 返回 True 即使没有记录被删除
        except Exception as e:
            print(f"删除场景下所有角色关联失败: {e}")
            return False


if __name__ == '__main__':
    # 测试get_character_scene_by_scene_id方法
    mapper = CharacterSceneMapper()
    scene_id = "1"  # 测试场景ID
    # print(mapper.is_character_in_scene(3, "2"))
    mapper.connect_character_2_scene(CharacterSceneRecord(character_id=10, sid="2", sort_order=1))

    # results = mapper.get_character_scene_by_scene_id(scene_id)

    # print(f"场景ID {scene_id} 下的角色场景记录:")
    # for record in results:
    #     print(f"  - 角色场景ID: {record.character_scene_id}, 角色ID: {record.character_id}, "
    #           f"场景ID: {record.sid}, 排序: {record.sort_order}")
    #
    # print(f"总共找到 {len(results)} 条记录")
