import logging
from abc import ABC
from typing import List, Optional

from config.Logger import logger
from entity.BaseModel import Conversation, Conversation2db, Character2db
from mapper.config.LoadDB import load_sqlite_config


class ConversationMapperInterface(ABC):

    def create_conversation(self, conv: Conversation) -> bool:
        raise NotImplementedError

    def get_conversations_by_character_id(self, character_id: int) -> List[Conversation]:
        raise NotImplementedError

    def get_conversation_by_scene_id(self, sid: str) -> List[Conversation]:
        raise NotImplementedError

    def update_conversation_by_id(self, conversation_id: int, conversation: Conversation) -> Conversation:
        raise NotImplementedError

    def delete_conversation_by_id(self, conversation_id: int) -> bool:
        raise NotImplementedError


class ConversationMapper(ConversationMapperInterface):
    def __init__(self):
        self.db = load_sqlite_config()
    
    def create_conversation(self, conv: Conversation) -> bool:
        """
        创建新的对话记录
        :param conv: Conversation对象
        :return: 创建成功返回True，失败返回False
        """
        try:
            # 获取发送者角色
            sender = Character2db.get_by_id(conv.sender_id)
            
            # 创建数据库记录
            conversation_db = Conversation2db.create(
                message=conv.message,
                sid=conv.sid,
                role=conv.role,
                sender=sender
            )
            # 更新conv对象的id
            conv.id = conversation_db.id
            return True
        except Exception as e:
            print(f"创建对话记录失败: {e}")
            return False
    
    def get_conversations_by_character_id(self, character_id: int) -> List[Conversation]:
        """
        根据角色ID获取所有对话记录
        :param character_id: 角色ID
        :return: 对话记录列表
        """
        try:
            conversations = []
            # 查询数据库
            query = Conversation2db.select().where(Conversation2db.sender == character_id)
            
            for conv_db in query:
                conv = Conversation(
                    message=conv_db.message,
                    sid=conv_db.sid,
                    sender_id=conv_db.sender.id,
                    role=conv_db.role,
                    conversation_id=conv_db.id
                )
                conversations.append(conv)
            
            return conversations
        except Exception as e:
            print(f"根据角色ID获取对话记录失败: {e}")
            return []
    
    def get_conversation_by_scene_id(self, sid: str) -> List[Conversation]:
        """
        根据场景ID获取所有对话记录
        :param sid: 场景ID
        :return: 对话记录列表
        """
        try:
            conversations = []
            # 查询数据库
            query = Conversation2db.select().where(Conversation2db.sid == sid)
            
            for conv_db in query:
                conv = Conversation(
                    message=conv_db.message,
                    sid=conv_db.sid,
                    sender_id=conv_db.sender.id,
                    role=conv_db.role,
                    conversation_id=conv_db.id
                )
                conversations.append(conv)
            
            return conversations
        except Exception as e:
            logger.error(f"根据场景ID获取对话记录失败: {e}")
            return []
    
    def update_conversation_by_id(self, conversation_id: int, conversation: Conversation) -> Optional[Conversation]:
        """
        根据ID更新对话记录
        :param conversation_id: 对话记录ID
        :param conversation: 更新的对话内容
        :return: 更新后的对话记录，失败返回None
        """
        try:
            # 获取要更新的记录
            conv_db = Conversation2db.get_by_id(conversation_id)
            
            # 获取发送者角色
            sender = Character2db.get_by_id(conversation.sender_id)
            
            # 更新字段
            conv_db.message = conversation.message
            conv_db.sid = conversation.sid
            conv_db.role = conversation.role
            conv_db.sender = sender
            conv_db.save()
            
            # 返回更新后的对话记录
            updated_conv = Conversation(
                message=conv_db.message,
                sid=conv_db.sid,
                sender_id=conv_db.sender.id,
                role=conv_db.role,
                conversation_id=conv_db.id
            )
            
            return updated_conv
        except Exception as e:
            print(f"更新对话记录失败: {e}")
            return None
    
    def delete_conversation_by_id(self, conversation_id: int) -> bool:
        """
        根据ID删除对话记录
        :param conversation_id: 对话记录ID
        :return: 删除成功返回True，失败返回False
        """
        try:
            # 获取并删除记录
            conv_db = Conversation2db.get_by_id(conversation_id)
            conv_db.delete_instance()
            return True
        except Exception as e:
            print(f"删除对话记录失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    mapper = ConversationMapper()
    
    # 创建测试对话
    test_conv = Conversation(
        message="这是一条测试消息",
        sid="1",
        sender_id=1,
        role="user"
    )
    
    # 测试创建对话
    result = mapper.create_conversation(test_conv)
    print(f"创建对话结果: {result}, 对话ID: {test_conv.id}")
    
    # 测试根据角色ID获取对话
    conversations = mapper.get_conversations_by_character_id(1)
    print(f"角色1的对话数量: {len(conversations)}")
    
    # 测试根据场景ID获取对话
    scene_conversations = mapper.get_conversation_by_scene_id("1")
    print(f"场景1的对话数量: {len(scene_conversations)}")
    
    # 测试更新对话
    if test_conv.id:
        test_conv.message = "更新后的消息"
        updated_conv = mapper.update_conversation_by_id(test_conv.id, test_conv)
        print(f"更新后的消息: {updated_conv.message if updated_conv else '更新失败'}")
    
    # 测试删除对话
    # if test_conv.id:
    #     delete_result = mapper.delete_conversation_by_id(test_conv.id)
    #     print(f"删除对话结果: {delete_result}")
