from typing import List

from entity.Scene import Scene, Graph
from entity.dto.CharacterSceneDTO import CharacterSceneDto
from mapper.CharacterMapper import CharacterMapper
from mapper.CharacterSceneMapper import CharacterSceneMapperInterface, CharacterSceneMapper
from mapper.SceneMapper import SceneMapperInterface, SceneMapper


class SceneService:
    """
    场景有关的service
    """
    def __init__(self, scene_mapper: SceneMapperInterface, character_mapper: CharacterMapper, 
                 character_scene_mapper: CharacterSceneMapperInterface):
        self._scene_mapper = scene_mapper
        self._character_mapper = character_mapper
        self._character_scene_mapper = character_scene_mapper

    def connect_character_2_scene(self, character_id: int, scene_id: str, sort_order: int = 0, is_visible: bool = True):
        """
        将角色信息与场景信息连接起来
        :param character_id: 角色id
        :param scene_id: 场景id
        :param sort_order: 角色排序
        :param is_visible: 角色在场景中是否可见
        :return: bool
        """
        from entity.BaseModel import CharacterSceneRecord
        return self._character_scene_mapper.connect_character_2_scene(
            CharacterSceneRecord(
                character_id=character_id,
                sid=scene_id,
                sort_order=sort_order,
                is_visible=is_visible
            )
        )

    def get_scene_by_id(self, scene_id: str) -> Scene:
        """
        根据场景id获取场景信息
        :param scene_id: 场景id
        :return: 场景信息
        """
        return SceneMapper.reverse(self._scene_mapper.get_scene_by_id(scene_id))

    def create_scene_by_current_scene(self, new_scene: Scene, current_scenes_id: List[str] | str = None,
                                      character_ids: List[int] = None) -> Scene:
        """
        根据当前场景创建下一个情景，可多个情景融合
        :param new_scene: 新场景信息
        :param current_scenes_id: 当前场景id列表或单个场景id
        :param character_ids: 角色id列表，可为空。如果为空且提供了current_scenes_id，则继承当前场景的角色列表
        :return: 创建的新场景
        """
        # 创建场景
        if current_scenes_id is not None:
            if isinstance(current_scenes_id, str):
                current_scenes_id = [current_scenes_id]

            prev_scenes = [
                self._scene_mapper.get_scene_by_id(current_scene_id) for current_scene_id in current_scenes_id]

            current_scene_db = self._scene_mapper.create_scene(
                new_scene,
                prev_scenes)
        else:
            current_scene_db = self._scene_mapper.create_scene(new_scene)

        # 处理角色连接
        new_scene_instance = SceneMapper.reverse(current_scene_db)

        # 如果没有提供角色列表且提供了current_scenes_id，则继承当前场景的角色列表
        if character_ids is None and current_scenes_id is not None:
            if isinstance(current_scenes_id, str):
                current_scenes_id = [current_scenes_id]

            # 从第一个场景获取角色列表（假设多个场景的角色列表相同）
            character_scenes = self._scene_mapper.get_characters_by_scene(current_scenes_id[0], include_invisible=False)
            character_ids = [character_scene.character_id for character_scene in character_scenes]

        # 如果有角色列表，则连接角色到新场景
        if character_ids:
            for idx, character_id in enumerate(character_ids):
                self.connect_character_2_scene(
                    character_id=character_id,
                    scene_id=new_scene_instance.sid,
                    sort_order=idx,
                    is_visible=True
                )

        return new_scene_instance

    def get_characters_by_scene(self, scene_id: str, include_invisible: bool = False) -> List[CharacterSceneDto]:
        """
        根据场景id获取对应场景的角色信息
        :param scene_id: 场景id
        :param include_invisible: 是否包含不可见角色
        :return: CharacterSceneDto列表，包含角色信息和关联信息
        """
        character_scenes = self._scene_mapper.get_characters_by_scene(scene_id, include_invisible)
        character_scene_dtos = []

        for character_scene in character_scenes:
            # 获取角色信息
            character = self._character_mapper.get_character_by_id(character_scene.character_id)

            # 创建CharacterSceneDto，包含角色信息和关联信息
            character_scene_dto = CharacterSceneDto(
                character_id=character_scene.character_id,
                sid=character_scene.sid,
                sort_order=character_scene.sort_order,
                is_visible=character_scene.is_visible,
                parent_id=character_scene.parent_id,
                character_scene_id=character_scene.character_scene_id,
                character=character
            )
            character_scene_dtos.append(character_scene_dto)

        return character_scene_dtos

    def delete_scene_by_id(self, scene_id: str):
        """
        根据情景id删除对应的情景
        同时删除对应情景角色关联表中的所有相关记录
        :param scene_id: 情景id
        :return: bool
        """
        try:
            # 批量删除情景角色关联表中的所有相关记录
            self._character_scene_mapper.disconnect_all_characters_from_scene(scene_id)

            # 然后删除情景本身
            return self._scene_mapper.delete_scene(scene_id)
        except Exception as e:
            print(f"删除情景失败: {e}")
            return False

    def update_scene_by_id(self, scene_id: str, new_scene: Scene) -> Scene:
        """
        更新指定情景的信息
        :param scene_id: 情景id
        :param new_scene: 新情景
        :return: 更新后的情景
        """
        new_scene_db = self._scene_mapper.update_scene_by_id(scene_id, new_scene)
        return SceneMapper.reverse(new_scene_db)

    def get_all_parents_by_id(self, sid: str) -> List[List[Scene]]:
        """
        获取指定情景的全部前情景
        :param sid: 情景id
        :return: 情景列表，若有融合情景节点则会有条情景链
        """
        all_parents = self._scene_mapper.get_all_parents_by_id(sid)
        return [[SceneMapper.reverse(parent) for parent in all_parent] for all_parent in all_parents]

    def get_all_scenes_graph(self) -> Graph:
        return self._scene_mapper.get_all_scenes_graph()


if __name__ == '__main__':
    scene_service = SceneService(
        scene_mapper=SceneMapper(),
        character_mapper=CharacterMapper(),
        character_scene_mapper=CharacterSceneMapper()
    )

    graph = scene_service.get_all_scenes_graph()
    print(graph.to_dict())
