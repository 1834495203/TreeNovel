from dataclasses import dataclass
from typing import List, Optional

from peewee import Model, CharField, ForeignKeyField, IntegerField, BooleanField

from mapper.config.LoadDB import load_sqlite_config


class BaseDtoModel(Model):
    class Meta:
        database = load_sqlite_config()


class Character2db(BaseDtoModel):
    name = CharField()

    prompt = CharField()

    # 是否可见
    is_visible = BooleanField(default=False)


@dataclass
class Character:
    name: str
    prompt: str
    is_visible: bool
    character_id: Optional[int] = None


class Conversation2db(BaseDtoModel):
    message = CharField()
    
    # 与scene表关联
    sid = CharField()

    role = CharField()

    sender = ForeignKeyField(Character2db, backref='sender_conversations', on_delete='CASCADE')


@dataclass
class Conversation:
    model_config = {"frozen": False}  # 可选：允许修改字段

    message: str
    sid: str
    sender_id: int
    role: str
    conversation_id: Optional[int] = None


@dataclass
class ConversationRecord:
    name: str
    character_id: int
    role: str
    content: str
    recipient: List[str]
    broadcast: bool
    time: int
    scene_id: str
    conversation_id: Optional[int] = None


# 角色与情景的关联表
class CharacterScene(BaseDtoModel):
    character_id = IntegerField()
    sid = CharField()

    # 根据character_id 确定排序
    sort_order = IntegerField()

    # 场景中角色是否可见
    is_visible = BooleanField(default=True)

    # 当character更新时，确保能连接到之前的character
    parent_id = ForeignKeyField(
        'self',  # 指向自身
        null=True,  # 可以为空
        backref='children',  # 反向引用，方便获取所有子节点
        on_delete='SET NULL'  # 如果父节点被删除，设置为NULL
    )


@dataclass
class   CharacterSceneRecord:
    character_id: int
    sid: str
    sort_order: int
    is_visible: bool = True
    parent_id: Optional[int] = None
    character_scene_id: Optional[int] = None


# 指令模板
class Template2db(BaseDtoModel):
    # 模板名字
    name = CharField()

    # 具体内容
    content = CharField()

    # 级别 system user
    garde = CharField()


@dataclass
class TemplateRecord:
    name: str
    content: str
    grade: str


if __name__ == '__main__':
    db = load_sqlite_config()
    db.connection()
    db.create_tables([Character2db, Conversation2db, CharacterScene, Template2db])
