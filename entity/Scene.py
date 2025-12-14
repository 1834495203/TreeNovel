from typing import Optional, List, Dict

from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom


class Scene4db(StructuredNode):
    sid = StringProperty(unique=True)
    name = StringProperty(unique_index=True)
    is_main = IntegerProperty()
    summary = StringProperty()
    is_root = IntegerProperty()

    # 定义一个有向关系，表示 'HAS_CHILD'。一个场景可以有多个子场景。
    children = RelationshipTo('Scene4db', 'HAS_CHILD')
    # 反向关系
    parents = RelationshipFrom('Scene4db', 'HAS_CHILD')


class Node:
    def __init__(self, sid: str):
        self.sid = sid


class Scene(Node):
    def __init__(self, sid: str, name: str, is_main: bool, summary: str, is_root: bool):
        super().__init__(sid)
        self.name = name
        self.is_main = is_main
        self.summary = summary
        self.is_root = is_root

    def __repr__(self):
        return f"Scene(sid={self.sid}, name={self.name}, is_main={self.is_main}, is_root={self.is_root})"


class Edge:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target

    def __repr__(self):
        return f"Edge({self.source} -> {self.target})"


class Graph:
    def __init__(self, nodes: Optional[List[Scene]] = None, edges: Optional[List[Edge]] = None):
        self.nodes: List[Scene] = nodes or []
        self.edges: List[Edge] = edges or []

    def add_node(self, node: Scene):
        self.nodes.append(node)

    def add_edge(self, source: str, target: str):
        self.edges.append(Edge(source, target))

    def to_dict(self) -> Dict:
        return {
            "nodes": [vars(n) for n in self.nodes],
            "edges": [{"source": e.source, "target": e.target} for e in self.edges],
        }

    def __repr__(self):
        return f"Graph(nodes={len(self.nodes)}, edges={len(self.edges)})"
