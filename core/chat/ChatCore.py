from abc import ABC, abstractmethod
from typing import Union, Generator, List

from entity.BaseModel import Conversation
from langchain_core.messages import BaseMessage


class ChatCore(ABC):

    @abstractmethod
    def prepare_context(self,
                       scene_id: str,
                       roleplay_character_id: int,
                       user_character_id: int,
                       is_current_scene: bool = False) -> List[BaseMessage]:
        """
        准备聊天上下文，包括角色设定、历史对话等

        Args:
            scene_id: 情景ID
            roleplay_character_id: LLM扮演的角色ID
            user_character_id: 用户扮演的角色ID
            is_current_scene: 是否限制在当前情景中a

        Returns:
            List[BaseMessage]: 准备好的langchain消息列表
        """
        raise NotImplementedError

    def generate_reply(self,
                       roleplay_character_id: int,
                       conversation: Conversation,
                       stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        与角色进行对话

        Args:
            roleplay_character_id: llm扮演的角色ID
            conversation: 对话内容
            stream: 是否流式返回，默认为False

        Returns:
            Union[str, Generator[str, None, None]]: 返回完整响应或流式响应生成器
        """
        raise NotImplementedError
