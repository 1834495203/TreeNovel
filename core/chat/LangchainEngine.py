import os

from dotenv import load_dotenv
from typing import Union, Generator, List

from config.Logger import logger
from core.PrepareChatHistory import PrepareChatHistory, build_chat_history_with_role_switch
from core.chat.ChatCore import ChatCore
from core.chat.Exceptions import ServerSideError
from entity.BaseModel import Conversation
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage

from mapper.CharacterMapper import CharacterMapper
from mapper.ConversationMapper import ConversationMapper
from mapper.SceneMapper import SceneMapper


from langchain_community.chat_models import ChatZhipuAI


class LangchainEngine(ChatCore):

    def __init__(self, prepare_chat_history: PrepareChatHistory):
        self.prepare_chat_history = prepare_chat_history

        load_dotenv()

        # 初始化LLM
        self.llm = ChatOpenAI(
            # model="kimi-k2-0905-preview",
            # model="glm-4.6",
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            # base_url="https://openrouter.ai/api/v1",
            # base_url="https://api.moonshot.cn/v1",
            base_url="https://api.deepseek.com",
            # base_url="https://open.bigmodel.cn/api/paas/v4",
            temperature=1,
        )

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
            is_current_scene: 是否限制在当前情景中

        Returns:
            List[BaseMessage]: 准备好的langchain消息列表
        """
        # 使用PrepareChatHistory准备聊天历史上下文
        chat_history = self.prepare_chat_history.prepared_chat_history(
            scene_id=scene_id,
            roleplay_character_id=roleplay_character_id,
            user_character_id=user_character_id,
            build_chat_callback=build_chat_history_with_role_switch,
            character_mapper=self.prepare_chat_history.character_mapper,
            is_current_scene=is_current_scene
        )

        return chat_history

    def generate_reply(self,
                       roleplay_character_id: int,
                       conversation: Conversation,
                       stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        与角色进行对话

        Args:
            roleplay_character_id: LLM扮演的角色ID
            conversation: 对话内容（包含当前用户消息）
            stream: 是否流式返回，默认为False

        Returns:
            Union[str, Generator[str, None, None]]: 返回完整响应或流式响应生成器
        """
        try:
            # 获取用户角色ID（从conversation的sender_id获取）
            user_character_id = conversation.sender_id

            # 准备聊天历史上下文
            chat_history = self.prepare_context(
                scene_id=conversation.sid,
                roleplay_character_id=roleplay_character_id,
                user_character_id=user_character_id,
                is_current_scene=False
            )

            logger.info(chat_history)

            if stream:
                # 流式响应
                def generate_response():
                    try:
                        # 调用LLM进行流式对话
                        response = self.llm.stream(chat_history)
                        chunk_count = 0
                        for chunk in response:
                            chunk_count += 1

                            # 尝试多种方式提取文本内容
                            content = None

                            # 方法1: 直接访问content属性
                            if hasattr(chunk, 'content') and chunk.content:
                                content = str(chunk.content)

                            # 方法2: 访问text属性
                            elif hasattr(chunk, 'text') and chunk.text:
                                content = str(chunk.text)

                            # 方法3: 访问message属性
                            elif hasattr(chunk, 'message') and chunk.message:
                                content = str(chunk.message)

                            # 方法4: 检查content_blocks（LangChain新版本格式）
                            elif hasattr(chunk, 'content_blocks') and chunk.content_blocks:
                                text_blocks = [b for b in chunk.content_blocks if b.get('type') == 'text']
                                if text_blocks:
                                    content = text_blocks[0].get('text', '')

                            # 方法5: 使用__str__作为最后手段（但要过滤AIMessage格式）
                            elif hasattr(chunk, '__str__'):
                                str_content = str(chunk)
                                # 过滤掉明显的AIMessage字符串格式
                                if not str_content.startswith('AIMessage(') and 'additional_kwargs' not in str_content:
                                    content = str_content

                            # 输出提取到的内容
                            if content:
                                yield content

                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"流式响应错误: {error_msg}")
                        # 抛出服务器端错误
                        raise ServerSideError(
                            message=f"流式响应错误: {error_msg}",
                            server_response=getattr(e, 'response', '') or error_msg
                        )

                return generate_response()
            else:
                # 非流式响应
                try:
                    response = self.llm.invoke(chat_history)
                    return response.content
                except Exception as e:
                    error_msg = str(e)
                    # 抛出服务器端错误，传入服务端返回的content
                    raise ServerSideError(
                        message=f"服务器端错误: {error_msg}",
                        server_response=getattr(e, 'response', '') or error_msg
                    )

        except ServerSideError:
            # 服务器端错误直接抛出，不进行处理
            raise
        except Exception as e:
            error_msg = str(e)
            # 抛出服务器端错误，传入服务端返回的content
            raise ServerSideError(
                message=f"服务器端错误: {error_msg}",
                server_response=getattr(e, 'response', '') or error_msg
            )


if __name__ == "__main__":
    prepare_chat_history = PrepareChatHistory(SceneMapper(), ConversationMapper(), CharacterMapper())
    engine = LangchainEngine(prepare_chat_history)
    resp = engine.generate_reply(
        roleplay_character_id=3,
        conversation=Conversation(message="我想去试穿衣服", sid="1", sender_id=1, role="user"),
        stream=True)

    for chunk in resp:
        print(chunk, end="")
