from abc import ABC
from typing import List, Optional

from neomodel import db

from config.Logger import logger
from entity.BaseModel import CharacterScene, CharacterSceneRecord
from entity.Scene import Scene4db, Scene, Graph
from mapper.config.LoadDB import load_neo4j_config


class SceneMapperInterface(ABC):

    def create_scene(self, scene: Scene, prev_scene4db: Optional[List[Scene4db]] = None) -> Scene4db:
        raise NotImplementedError

    def connect_scenes(self, target_scene4db: Scene4db, prev_scene4db: Optional[List[Scene4db]]) -> Scene4db:
        raise NotImplementedError

    def update_scene_by_id(self, sid: str, scene: Scene) -> Scene4db:
        raise NotImplementedError

    def get_scene_by_id(self, sid: str) -> Scene4db:
        raise NotImplementedError

    def get_all_parents_by_id(self, sid: str) -> List[List[Scene4db]]:
        raise NotImplementedError

    def delete_scene(self, scene_id: str) -> bool:
        raise NotImplementedError

    def get_all_scenes_graph(self) -> Graph:
        raise NotImplementedError

    def get_parents_by_id(self, scene_id: str) -> Optional[List[Scene4db]]:
        raise NotImplementedError

    def get_characters_by_scene(self, scene_id, include_invisible=False) -> List[CharacterSceneRecord]:
        raise NotImplementedError


class SceneMapper(SceneMapperInterface):
    def __init__(self):
        load_neo4j_config()

    @staticmethod
    def convert(scene: Scene) -> Scene4db:
        return Scene4db(sid=scene.sid, name=scene.name, is_main=scene.is_main, summary=scene.summary,
                        is_root=scene.is_root)

    @staticmethod
    def reverse(scene4db: Scene4db) -> Scene:
        return Scene(sid=scene4db.sid, name=scene4db.name, is_main=scene4db.is_main, summary=scene4db.summary,
                     is_root=scene4db.is_root)

    def create_scene(self, scene: Scene, prev_scene4db: Optional[List[Scene4db]] = None) -> Scene4db:
        scene4db = self.convert(scene)
        scene4db.save()
        if prev_scene4db:
            for prev in prev_scene4db:
                prev.children.connect(scene4db)
        return scene4db

    def connect_scenes(self, target_scene4db: Scene4db, prev_scene4db: Optional[List[Scene4db]]) -> Scene4db:
        for prev in prev_scene4db:
            prev.children.connect(target_scene4db)
        return target_scene4db

    def update_scene_by_id(self, sid: str, scene: Scene) -> Scene4db:
        scene_to_update = Scene4db.nodes.get(sid=sid)

        scene_to_update.name = scene.name
        scene_to_update.summary = scene.summary
        scene_to_update.is_main = scene.is_main

        scene_to_update.save()

        return scene_to_update

    def get_scene_by_id(self, sid: str) -> Scene4db:
        scene4db = Scene4db.nodes.get(sid=sid)
        return scene4db

    def get_parents_by_id(self, scene_id: str) -> Optional[List[Scene4db]]:
        current_scene = self.get_scene_by_id(scene_id)
        parents = current_scene.parents.all()
        return parents

    def get_all_parents_by_id(self, sid: str) -> List[List[Scene4db]]:
        """
        根据传入的sid，递归地寻找它的所有父节点路径，直到父节点为根节点。
        如果有多个父节点，则有多条链。

        :param sid: 场景的唯一标识符。
        :return: 一个包含所有父节点路径的列表。每条路径都是一个从当前场景到根场景的节点列表。
        """
        current_node = Scene4db.nodes.get(sid=sid)

        # 路径列表，用来存储所有完整的父节点路径
        all_paths = []
        # 递归查找的起始调用，传入当前节点和初始路径
        self._find_parent_paths(current_node, [current_node], all_paths)

        # 遍历所有找到的路径，并将其反转
        for path in all_paths:
            path.reverse()

        return all_paths

    def _find_parent_paths(self, node: Scene4db, current_path: List[Scene4db], all_paths: List[List[Scene4db]]):
        """
        递归帮助函数，用于寻找所有父节点路径。

        :param node: 当前正在处理的节点。
        :param current_path: 当前正在构建的路径。
        :param all_paths: 存储所有完整路径的列表。
        """
        # 检查当前节点是否为根节点
        if node.is_root == 1:
            # 如果是根节点，将当前路径的副本添加到结果列表中
            all_paths.append(list(current_path))
            return

        # 获取当前节点的所有父节点
        parents = list(node.parents.all())

        # 如果没有父节点且不是根节点，说明是孤立的节点，也将其路径添加到结果中（可选）
        if not parents:
            all_paths.append(list(current_path))
            return

        # 遍历所有父节点
        for parent_node in parents:
            # 创建新的路径，将父节点添加到其中
            new_path = current_path + [parent_node]
            # 递归调用，以父节点为新的起点继续向上查找
            self._find_parent_paths(parent_node, new_path, all_paths)

    def delete_scene(self, scene_id: str) -> bool:
        scene_to_delete = Scene4db.nodes.get(sid=scene_id)
        return scene_to_delete.delete()

    def get_all_scenes_graph(self) -> Graph:
        query = """
        MATCH (s:Scene4db)
        OPTIONAL MATCH (s)-[r:HAS_CHILD]->(c:Scene4db)
        RETURN s, collect({rel:r, target:c}) as relations
        """
        results, _ = db.cypher_query(query)

        graph = Graph()

        for row in results:
            scene_node = Scene4db.inflate(row[0])
            scene = self.reverse(scene_node)
            graph.add_node(scene)

            relations = row[1]
            for rel in relations:
                if rel["rel"] is not None and rel["target"] is not None:
                    child_node = Scene4db.inflate(rel["target"])
                    graph.add_edge(scene.sid, child_node.sid)

        return graph

    def get_characters_by_scene(self, scene_id, include_invisible=False) -> List[CharacterSceneRecord]:
        """
        获取指定情景中的所有角色ID

        :param scene_id: 情景ID
        :param include_invisible: 是否包含不可见角色，默认为False
        :return: 角色ID列表
        """
        query = CharacterScene.select().where(CharacterScene.sid == scene_id)
        if not include_invisible:
            query = query.where(CharacterScene.is_visible == True)
        
        results = query.execute()
        character_scene_record = []
        for result in results:
            character_scene_record.append(
                CharacterSceneRecord(
                    character_id=result.character_id,
                    sid=result.sid,
                    sort_order=result.sort_order,
                    is_visible=result.is_visible,
                    parent_id=result.parent_id,
                    character_scene_id=result.id))
        return character_scene_record


def create_graph():
    scene_mapper = SceneMapper()
    root = Scene(sid="1", name="root", is_main=True, is_root=True, summary="")
    scene1 = Scene(sid="2", name="test1", is_main=True, is_root=False, summary="")
    scene2 = Scene(sid="3", name="test2", is_main=False, is_root=False, summary="")
    scene3 = Scene(sid="4", name="test3", is_main=True, is_root=False, summary="")

    scene_mapper.create_scene(root)
    # scene_mapper.create_scene(scene1, [scene_mapper.get_scene_by_id(1)])
    # scene_mapper.create_scene(scene2, [scene_mapper.get_scene_by_id(1)])
    # scene_mapper.create_scene(scene3, [scene_mapper.get_scene_by_id(2), scene_mapper.get_scene_by_id(3)])


if __name__ == '__main__':
    scene_mapper = SceneMapper()
    scene_mapper.get_characters_by_scene("2")
    # root = Scene(sid="2", name="root", is_main=True, is_root=True, summary="hello world")
    # scene_mapper.create_scene(root)
