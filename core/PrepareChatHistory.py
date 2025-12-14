from abc import ABC
from typing import List, Callable, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

from config.Logger import logger
from entity.BaseModel import Conversation
from entity.Scene import Scene4db
from mapper.CharacterMapper import CharacterMapper
from mapper.CharacterSceneMapper import CharacterSceneMapper
from mapper.ConversationMapper import ConversationMapper
from mapper.SceneMapper import SceneMapper


# 定义回调函数类型
BuildChatHistoryCallback = Callable[
    [List[BaseMessage], List[Conversation], Any],  # Any 用于接收额外的 kwargs
    List[BaseMessage]
]


def default_build_chat_history(
    langchain_messages: List[BaseMessage],
    chat_message: List[Conversation],
    **kwargs  # 支持任意额外参数
) -> List[BaseMessage]:
    """默认的聊天历史构建函数"""
    for conversation in chat_message:
        if conversation.role == "user":
            langchain_messages.append(HumanMessage(content=conversation.message))
        elif conversation.role == "assistant":
            langchain_messages.append(AIMessage(content=conversation.message))
    return langchain_messages


def build_chat_history_with_role_switch(
        langchain_messages: List[BaseMessage],
        chat_message: List[Conversation],
        **kwargs
) -> List[BaseMessage]:
    """
    构建聊天历史，并在角色切换时添加系统提示消息

    参数:
        langchain_messages: 已有的 langchain 消息列表
        chat_message: 对话历史列表
        **kwargs: 额外参数，需要包含:
            - character_mapper: CharacterMapper 实例，用于获取角色名称
            - roleplay_character_id: int, LLM 扮演的角色 ID

    返回:
        List[BaseMessage]: 构建好的消息列表
    """
    character_mapper: CharacterMapper = kwargs.get('character_mapper')
    roleplay_character_id: int = kwargs.get('roleplay_character_id')

    if not character_mapper:
        raise ValueError("character_mapper is required in kwargs")
    if roleplay_character_id is None:
        raise ValueError("roleplay_character_id is required in kwargs")

    # 用于追踪上一个user和assistant的sender_id
    last_user_sender_id = None
    last_assistant_sender_id = None

    for conversation in chat_message:
        if conversation.role == "user":
            # 检查是否需要添加用户角色切换提示
            if last_user_sender_id is not None and last_user_sender_id != conversation.sender_id:
                # 获取角色名称
                old_character = character_mapper.get_character_by_id(last_user_sender_id)
                new_character = character_mapper.get_character_by_id(conversation.sender_id)

                # 添加系统消息提示角色切换
                switch_message = f"用户从 [{old_character.name}] 切换至 [{new_character.name}]"
                langchain_messages.append(SystemMessage(content=switch_message))

            # 更新最后的user sender_id
            last_user_sender_id = conversation.sender_id

            # 添加用户消息
            langchain_messages.append(HumanMessage(content=conversation.message))

        elif conversation.role == "assistant":
            # 检查是否需要添加LLM角色切换提示
            if last_assistant_sender_id is not None and last_assistant_sender_id != conversation.sender_id:
                # 获取角色名称
                old_character = character_mapper.get_character_by_id(last_assistant_sender_id)
                new_character = character_mapper.get_character_by_id(conversation.sender_id)

                # 添加系统消息提示LLM角色切换
                switch_message = f"llm从 [{old_character.name}] 切换至 [{new_character.name}]"
                langchain_messages.append(SystemMessage(content=switch_message))

            # 检查最后一条assistant消息的sender_id是否与roleplay_character_id一致
            # 这个检查只在处理最后一条assistant消息时才有意义
            # 我们在循环中记录，但实际的不一致提示可以在外部处理

            # 更新最后的assistant sender_id
            last_assistant_sender_id = conversation.sender_id

            # 添加AI消息
            langchain_messages.append(AIMessage(content=conversation.message))

    # 检查最后一条assistant消息的sender_id是否与roleplay_character_id一致
    if last_assistant_sender_id is not None and last_assistant_sender_id != roleplay_character_id:
        old_character = character_mapper.get_character_by_id(last_assistant_sender_id)
        new_character = character_mapper.get_character_by_id(roleplay_character_id)

        switch_message = f"llm从 [{old_character.name}] 切换至 [{new_character.name}]"
        langchain_messages.append(SystemMessage(content=switch_message))

    return langchain_messages


class PrepareChatHistoryInterface(ABC):
    """
    该类专门组装上下文信息
    """

    def get_pre_chat_history_by_scene(self, scene_id: str) -> str:
        """
        最初的上下文，定义角色，世界观等信息
        :param scene_id: 情景id，需要获取对应连接的角色或世界观设定等信息
        :return: 上下文
        """
        raise NotImplementedError

    def get_chat_history_by_scene(self, scene_id: str) -> List[Conversation]:
        """
        获取指定情景id中的聊天信息，取决于角色聊天
        :param scene_id: 情景id
        :return: 聊天记录
        """
        raise NotImplementedError

    def get_all_chat_history_by_scene(self, scene_id: str, all_scenes: List[Scene4db],
                                      roleplay_character_id: int) -> tuple[str, List[Conversation]]:
        """
        获取包括此情景在内的所有前情景的聊天信息
        :param scene_id: 情景id
        :param all_scenes: 情景链
        :param roleplay_character_id: llm扮演的角色id
        :return: 两个参数，第一个是全局上下文，第二个是全部的聊天记录
        """
        raise NotImplementedError

    def prepared_chat_history(self, scene_id: str,
                              roleplay_character_id: int,
                              user_character_id: int,
                              is_current_scene: bool = True,
                              build_chat_callback: Optional[BuildChatHistoryCallback] = None,
                              **build_kwargs
                              ):
        """
        将所有上下文结合起来，并要求llm的扮演角色
        :param scene_id: 情景id
        :param roleplay_character_id: 需要扮演的角色
        :param user_character_id: user扮演的角色
        :param is_current_scene: 是否将上下文和聊天记录限制在当前情景中
        :param build_chat_callback: 自定义构建对话上下文的方式
        :param build_kwargs: 传递给回调函数的额外参数
        :return: langchain式的上下文
        """
        raise NotImplementedError


class PrepareChatHistory(PrepareChatHistoryInterface):

    def __init__(self, scene_mapper: SceneMapper,
                 conversation_mapper: ConversationMapper,
                 character_mapper: CharacterMapper,
                 character_scene_mapper: CharacterSceneMapper,):
        self.scene_mapper = scene_mapper
        self.conversation_mapper = conversation_mapper
        self.character_mapper = character_mapper
        self.char_scene_mapper = character_scene_mapper

    def _is_character_in_scene(self, character_id: int, scene_id: str) -> bool:
        """
        判断角色是否在指定情景中（只考虑可见角色）
        :param character_id: 角色ID
        :param scene_id: 情景ID
        :return: True表示角色在情景中且可见，False表示不在或不可见
        """
        characters_in_scene = self.scene_mapper.get_characters_by_scene(scene_id, include_invisible=True)
        return character_id in [character_scene.character_id for character_scene in characters_in_scene]

    def get_pre_chat_history_by_scene(self, scene_id: str):
        """
        获取指定情景的角色设定上下文（仅包含当前场景显式定义的可见角色）
        :param scene_id: 情景id
        :return: 角色设定上下文字符串
        """
        pre_chat_history = ""
        # 获取当前场景显式定义的角色关联记录
        character_scene_records = self.char_scene_mapper.get_character_scene_by_scene_id(scene_id, include_invisible=False)
        for record in character_scene_records:
            character = self.character_mapper.get_character_by_id(record.character_id)
            # 只添加可见角色的prompt
            if character.is_visible:
                pre_chat_history += character.prompt
                pre_chat_history += "\n --- \n"
        return pre_chat_history

    def get_chat_history_by_scene(self, scene_id: str, roleplay_character_id: Optional[int] = None):
        """
        获取指定情景中的聊天记录
        根据角色可见性和情景可见性进行过滤：
        1. 情景可见性：如果指定了roleplay_character_id，只有该角色在情景中时，该情景才可见
        2. 角色可见性：只返回is_visible=True的角色的对话

        :param scene_id: 情景id
        :param roleplay_character_id: llm扮演的角色ID，用于判断情景是否可见
        :return: 聊天记录列表
        """
        # 情景可见性检查：如果指定了roleplay_character_id，需要判断该角色是否在情景中
        # 如果不在情景中，则该情景的对话对该角色不可见，返回空列表
        if roleplay_character_id is not None:
            if not self._is_character_in_scene(roleplay_character_id, scene_id):
                return []
        # 获取该情景的所有对话
        conversations = self.conversation_mapper.get_conversation_by_scene_id(scene_id)

        # 角色可见性过滤：只返回可见角色的对话
        visible_conversations = [
            conv for conv in conversations
            if self.character_mapper.get_character_by_id(conv.sender_id).is_visible
        ]

        return visible_conversations

    def prepared_chat_history(self, scene_id: str,
                              roleplay_character_id: int,
                              user_character_id: int,
                              is_current_scene: bool = True,
                              build_chat_callback: Optional[BuildChatHistoryCallback] = None,
                              **build_kwargs
                              ):
        """
        组装完整的聊天上下文，包括角色设定、历史对话和角色扮演指令

        整体逻辑：
        1. 获取情景链（从旧到新）
        2. 根据is_current_scene决定是否只使用当前情景的上下文
        3. 检查角色是否首次出现，决定是否需要完整的角色介绍
        4. 组装langchain消息列表，包括：
           - 系统消息（角色设定和世界观）
           - 历史对话（通过回调函数构建）
           - 角色扮演指令
           - 强制姓名标签指令

        :param scene_id: 情景id
        :param roleplay_character_id: LLM需要扮演的角色ID
        :param user_character_id: 用户扮演的角色ID
        :param is_current_scene: 是否将上下文限制在当前情景中
        :param build_chat_callback: 自定义构建对话上下文的回调函数
        :param build_kwargs: 传递给回调函数的额外参数
        :return: langchain格式的消息列表
        """
        # 使用默认回调函数（如果未指定）
        if build_chat_callback is None:
            build_chat_callback = default_build_chat_history

        # 获取情景链（默认只有一条，需要考虑多分支合并）
        all_scenes = self.scene_mapper.get_all_parents_by_id(scene_id)[0]
        # 反转为从最新到最旧的顺序，方便后续处理
        all_scenes.reverse()

        all_scenes_id = [scene.sid for scene in all_scenes]

        # 根据is_current_scene决定获取哪些情景的上下文和对话
        if is_current_scene:
            # 只获取当前情景的上下文和对话
            # 检查llm角色是否在当前情景中
            if not self._is_character_in_scene(roleplay_character_id, scene_id):
                raise ValueError(f"角色 {roleplay_character_id} 不在情景 {scene_id} 中，无法准备聊天历史")

            pre_chat = self.get_pre_chat_history_by_scene(scene_id)
            chat_message = self.get_chat_history_by_scene(scene_id, roleplay_character_id)
        else:
            # 获取所有情景的上下文和对话（已包含情景可见性和角色可见性过滤）
            pre_chat, chat_message = self.get_all_chat_history_by_scene(scene_id, all_scenes, roleplay_character_id)

        # 检查角色是否首次出现在情景链中
        # 如果是首次出现（返回None），则需要完整的角色prompt
        # 如果不是首次出现，则不重复显示角色prompt（因为在pre_chat中已经包含了）
        first_roleplay_character = self.char_scene_mapper.character_first_in_any_scenes(
            roleplay_character_id, all_scenes_id)
        first_user_roleplay_character = self.char_scene_mapper.character_first_in_any_scenes(
            user_character_id, all_scenes_id
        )

        # 获取角色信息
        roleplay_character = self.character_mapper.get_character_by_id(roleplay_character_id)
        user_roleplay_character = self.character_mapper.get_character_by_id(user_character_id)

        # 根据是否首次出现决定是否添加角色prompt
        # 首次出现时，first_xxx为None，此时显示完整prompt
        # 非首次出现时，first_xxx不为None，此时不显示prompt（避免重复）
        roleplay_character_prompt = roleplay_character.prompt if first_roleplay_character is None else ""
        user_roleplay_prompt = user_roleplay_character.prompt if first_user_roleplay_character is None else ""

        # 创建langchain消息列表
        langchain_messages = []

        # 第一部分：添加世界观和角色设定（来自情景中的所有可见角色）
        system_content = f"{pre_chat}"
        langchain_messages.append(SystemMessage(content=system_content))

        # 第二部分：通过回调函数构建历史对话
        langchain_messages = build_chat_callback(langchain_messages,
                                                 chat_message,
                                                 scene_id=scene_id,
                                                 roleplay_character_id=roleplay_character_id,
                                                 user_character_id=user_character_id,
                                                 is_current_scene=is_current_scene,
                                                 **build_kwargs)

        # 第三部分：添加角色扮演指令
        langchain_messages.append(SystemMessage(
            content=f"你是{roleplay_character.name}, {roleplay_character_prompt} \n "
                    f"用户将扮演{user_roleplay_character.name}, {user_roleplay_prompt}"))

        # 第四部分：添加强制姓名标签指令
        langchain_messages.append(
            SystemMessage(
                content=f"你的回复开头必须包含你扮演角色的真实姓名的标签，且禁止使用代号，绰号，小名等。"
                        f"示例：[{roleplay_character.name}] \\n "))

        return langchain_messages

    def get_all_chat_history_by_scene(self, scene_id: str, all_scenes: List[Scene4db],
                                      roleplay_character_id: int) -> tuple[str, List[Conversation]]:
        """
        获取包括此情景在内的所有前情景的聊天信息
        根据情景可见性和角色可见性进行过滤：
        1. 情景可见性：只包含roleplay_character在其中的情景
        2. 角色可见性：每个情景只包含该情景显式定义的可见角色
        3. 移除继承逻辑：每个场景的角色完全由该场景显式定义

        :param scene_id: 情景id
        :param all_scenes: 情景链（从旧到新排序）
        :param roleplay_character_id: llm扮演的角色ID，用于判断情景可见性
        :return: (全局角色上下文, 聊天记录列表)
        """
        chat_history = []

        # 只获取当前场景的角色上下文，不再继承之前场景的角色
        # 因为每个场景的角色现在完全由该场景显式定义
        current_scene = next((scene for scene in all_scenes if scene.sid == scene_id), None)
        if not current_scene:
            return "", []

        # 检查当前场景是否对roleplay_character可见
        if not self._is_character_in_scene(roleplay_character_id, current_scene.sid):
            return "", []

        # 获取当前场景显式定义的角色上下文
        pre_chat_history = self.get_pre_chat_history_by_scene(current_scene.sid)

        # 获取聊天历史：
        # 1. 遍历所有情景
        # 2. 如果该情景对llm扮演的角色可见，则加载该情景的所有可见角色对话

        for scene in all_scenes:
            # 检查该情景是否对llm扮演的角色可见（即该角色是否在该情景中）
            if not self._is_character_in_scene(roleplay_character_id, scene.sid):
                continue

            # 获取该情景中所有可见角色的对话
            scene_conversations = self.get_chat_history_by_scene(scene.sid, roleplay_character_id)

            # 将该情景的对话插入到列表开头，保持时间顺序
            chat_history[:0] = scene_conversations

        return pre_chat_history, chat_history


if __name__ == '__main__':
    prepare_chat_history = PrepareChatHistory(
        SceneMapper(), ConversationMapper(), CharacterMapper(), CharacterSceneMapper())

    context = prepare_chat_history.prepared_chat_history(
        scene_id="1",
        roleplay_character_id=3,
        user_character_id=1,
        is_current_scene=False,
        build_chat_callback=build_chat_history_with_role_switch,
        character_mapper=prepare_chat_history.character_mapper,
    )
    print(context)
