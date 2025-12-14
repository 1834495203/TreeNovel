from abc import ABC
from typing import List, Optional

from entity.BaseModel import Conversation
from mapper.ConversationMapper import ConversationMapper, ConversationMapperInterface


class ConversationServiceInterface(ABC):

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """
        创建新对话

        Args:
            conversation: 对话信息

        Return:
            创建的对话

        Raises:
            Exception: 创建对话失败
        """
        raise NotImplementedError

    def get_conversations_by_character_id(self, character_id: int) -> List[Conversation]:
        """
        根据角色ID获取对话列表

        Args:
            character_id: 角色ID

        Return:
            对话列表
        """
        raise NotImplementedError

    def get_conversations_by_scene_id(self, scene_id: str) -> List[Conversation]:
        """
        根据场景ID获取对话列表

        Args:
            scene_id: 场景ID

        Return:
            对话列表
        """
        raise NotImplementedError

    def update_conversation(self, conversation_id: int, conversation: Conversation) -> Optional[Conversation]:
        """
        更新对话信息

        Args:
            conversation_id: 对话ID
            conversation: 新对话信息

        Return:
            更新后的对话，失败返回None
        """
        raise NotImplementedError

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        删除对话

        Args:
            conversation_id: 对话ID

        Return:
            是否删除成功
        """
        raise NotImplementedError


class ConversationService(ConversationServiceInterface):
    """
    对话相关的service
    """

    def __init__(self, conversation_mapper: ConversationMapperInterface):
        self._conversation_mapper = conversation_mapper

    def create_conversation(self, conversation: Conversation) -> Conversation:
        """
        创建新对话

        Args:
            conversation: 对话信息

        Return:
            创建的对话

        Raises:
            Exception: 创建对话失败
        """
        success = self._conversation_mapper.create_conversation(conversation)

        if success:
            return conversation
        else:
            raise Exception("创建对话失败")

    def get_conversations_by_character_id(self, character_id: int) -> List[Conversation]:
        """
        根据角色ID获取对话列表

        Args:
            character_id: 角色ID

        Return:
            对话列表
        """
        return self._conversation_mapper.get_conversations_by_character_id(character_id)

    def get_conversations_by_scene_id(self, scene_id: str) -> List[Conversation]:
        """
        根据场景ID获取对话列表

        Args:
            scene_id: 场景ID

        Return:
            对话列表
        """
        return self._conversation_mapper.get_conversation_by_scene_id(scene_id)

    def update_conversation(self, conversation_id: int, conversation: Conversation) -> Optional[Conversation]:
        """
        更新对话信息

        Args:
            conversation_id: 对话ID
            conversation: 新对话信息

        Return:
            更新后的对话，失败返回None
        """
        updated_conversation = self._conversation_mapper.update_conversation_by_id(conversation_id, conversation)

        if updated_conversation is None:
            raise Exception(f"更新对话 {conversation_id} 失败")

        return updated_conversation

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        删除对话

        Args:
            conversation_id: 对话ID

        Return:
            是否删除成功
        """
        return self._conversation_mapper.delete_conversation_by_id(conversation_id)


if __name__ == '__main__':
    conversation_service = ConversationService(ConversationMapper())
