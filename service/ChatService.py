from abc import ABC
from typing import Union, Generator

from config.Logger import logger
from core.chat.ChatCore import ChatCore
from entity.BaseModel import Conversation
from mapper.CharacterSceneMapper import CharacterSceneMapper
from mapper.ConversationMapper import ConversationMapper
from core.chat.LangchainEngine import LangchainEngine
from core.PrepareChatHistory import PrepareChatHistory
from mapper.SceneMapper import SceneMapper
from mapper.CharacterMapper import CharacterMapper
from utils.ToolKit import normalize_role_prefix


class ChatServiceInterface(ABC):

    def chat(self, roleplay_id: int, conversation: Conversation, stream: bool):
        raise NotImplementedError


class ChatService(ChatServiceInterface):
    """
    与对话聊天有关的service
    """
    def __init__(self,
                 chat_core: ChatCore,
                 conversation_mapper: ConversationMapper,
                 character_mapper: CharacterMapper,
                 character_scene_mapper: CharacterSceneMapper,
                 scene_mapper: SceneMapper,):
        self.group_agent_engine = chat_core
        self.conversation_mapper = conversation_mapper
        self.character_mapper = character_mapper
        self.character_scene_mapper = character_scene_mapper
        self.scene_mapper = scene_mapper

    def chat(self, roleplay_id: int, conversation: Conversation, stream: bool):
        """
        处理用户与角色的对话，并存储对话记录

        Args:
            roleplay_id: LLM扮演的角色ID
            conversation: 用户发送的对话内容
            stream: 是否流式返回响应

        Returns:
            dict: 包含响应内容、用户conversation_id和assistant conversation_id的字典
        """
        try:
            scenes_id = [scene.sid for scene in self.scene_mapper.get_all_parents_by_id(conversation.sid)[0]]

            if not (self.character_scene_mapper.is_character_in_any_scenes(roleplay_id, scenes_id) and
                    self.character_scene_mapper.is_character_in_any_scenes(conversation.sender_id, scenes_id)):
                raise ValueError("角色不在情景中！")

            # 1. 首先存储用户的对话到数据库, 检查角色标签
            conversation.message = normalize_role_prefix(
                conversation.message,
                role_name=self.character_mapper.get_character_by_id(conversation.sender_id).name)

            user_conversation_saved = self.conversation_mapper.create_conversation(conversation)
            if not user_conversation_saved:
                error_msg = "存储用户对话失败"
                if stream:
                    def error_generator():
                        yield error_msg
                    return {"error": error_msg}
                else:
                    return {"error": error_msg}

            # 保存用户conversation_id
            user_conversation_id = conversation.id

            # 2. 调用LLM生成回复
            llm_response = self.group_agent_engine.generate_reply(
                roleplay_character_id=roleplay_id,
                conversation=conversation,
                stream=stream
            )
            if stream:
                # 3. 流式响应处理
                # 预先创建assistant的conversation记录，获取conversation_id
                assistant_conversation_id = None
                llm_conversation = Conversation(
                    message="",  # 初始为空，流式更新
                    sid=conversation.sid,
                    sender_id=roleplay_id,  # LLM回复的发送者是roleplay角色
                    role="assistant",
                    conversation_id=None
                )
                saved = self.conversation_mapper.create_conversation(llm_conversation)
                if saved:
                    assistant_conversation_id = llm_conversation.id

                def stream_with_storage():
                    nonlocal assistant_conversation_id
                    full_response = ""
                    try:
                        # 收集完整的流式响应
                        for chunk in llm_response:
                            full_response += chunk
                            yield chunk

                        # 4. 存储LLM的完整回复到数据库
                        if full_response:
                            full_response = normalize_role_prefix(
                                full_response,
                                role_name=self.character_mapper.get_character_by_id(roleplay_id).name)

                            # 更新已创建的conversation记录
                            if assistant_conversation_id:
                                updated_conv = Conversation(
                                    message=full_response,
                                    sid=conversation.sid,
                                    sender_id=roleplay_id,
                                    role="assistant",
                                    conversation_id=assistant_conversation_id
                                )
                                self.conversation_mapper.update_conversation_by_id(assistant_conversation_id, updated_conv)

                    except Exception as e:
                        error_msg = f"流式响应处理失败: {str(e)}"
                        yield error_msg

                # 返回生成器和conversation_id
                return {
                    "stream": stream_with_storage(),
                    "user_conversation_id": user_conversation_id,
                    "assistant_conversation_id": assistant_conversation_id
                }

            else:
                # 3. 非流式响应处理
                assistant_conversation_id = None
                if isinstance(llm_response, str) and llm_response:
                    # 4. 存储LLM的回复到数据库
                    llm_conversation = Conversation(
                        message=llm_response,
                        sid=conversation.sid,
                        sender_id=roleplay_id,  # LLM回复的发送者是roleplay角色
                        role="assistant",
                        conversation_id=None
                    )
                    saved = self.conversation_mapper.create_conversation(llm_conversation)
                    if saved:
                        assistant_conversation_id = llm_conversation.id

                return {
                    "response": llm_response,
                    "user_conversation_id": user_conversation_id,
                    "assistant_conversation_id": assistant_conversation_id
                }

        except Exception as e:
            error_msg = f"对话处理失败: {str(e)}"
            logger.error(error_msg)
            if stream:
                def error_generator():
                    yield error_msg

                return {"error": error_msg, "stream": error_generator()}
            else:
                return {"error": error_msg}


if __name__ == "__main__":
    # 初始化依赖
    prepare_chat_history = PrepareChatHistory(SceneMapper(), ConversationMapper(), CharacterMapper(),
                                              CharacterSceneMapper())
    chat_core = LangchainEngine(prepare_chat_history)
    conversation_mapper = ConversationMapper()
    character_mapper = CharacterMapper()
    character_scene_mapper = CharacterSceneMapper()
    scene_mapper = SceneMapper()
    
    # 创建ChatService实例
    chat_service = ChatService(chat_core, conversation_mapper, character_mapper, character_scene_mapper, scene_mapper)

    scene_id = "2"
    scenes = scene_mapper.get_all_parents_by_id(scene_id)[0]
    for scene in scenes:
        print(f"===情景 · {scene.name}===")
        conversations = conversation_mapper.get_conversation_by_scene_id(scene.sid)
        for conversation in conversations:
            print(f"{character_mapper.get_character_by_id(conversation.sender_id).name}: {conversation.message}")
        print("===")

    while True:
        content = input("\n 请输入回答：")
    
        # 对话
        conversation = Conversation(
            message=content,
            sid=scene_id,
            sender_id=10,
            role="user"
        )

        stream_response = chat_service.chat(roleplay_id=3, conversation=conversation, stream=True)
        for chunk in stream_response:
            print(chunk, end="")
