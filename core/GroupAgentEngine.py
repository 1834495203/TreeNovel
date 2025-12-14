import os
import time
from typing import List, Any

from autogen import ConversableAgent, Agent
from dotenv import load_dotenv

from entity.BaseModel import Character, ConversationRecord
from entity.Scene import Scene


class UserProxyAgent(ConversableAgent):

    def __init__(self, character_id: int, **kwargs):
        super(UserProxyAgent, self).__init__(**kwargs)
        self.character_id = character_id

    def get_human_input(self, prompt: str) -> str:
        # 在该方法中修改用户输入对话的方式
        msg = input("输入对话\n")
        return msg

    def send(self, message: dict[str, Any] | str, recipient: Agent, request_reply: bool | None = None,
             silent: bool | None = False, is_resume=False):
        super().send(message, recipient, request_reply, silent)


class CharacterAgent(ConversableAgent):

    def __init__(self, character_id: int, **kwargs):
        super().__init__(**kwargs)
        self.character_id = character_id

    def send(self, message: dict[str, Any] | str, recipient: Agent, request_reply: bool | None = None,
             silent: bool | None = False, is_resume=False):
        # 在该方法中可以保存角色的对话
        if is_resume is False:
            print(f"{self.name} talk to {recipient.name}: {message}")
        super().send(message, recipient, request_reply, silent)

    def _generate_oai_reply_from_client(self, llm_client, messages, cache) -> str | dict[str, Any] | None:
        # print(f"messages before response: {messages}")
        return super()._generate_oai_reply_from_client(llm_client, messages, cache)


class CharacterGroupChat:
    def __init__(self, agents: List[CharacterAgent | UserProxyAgent | Agent], scene: Scene):
        self.agents = {agent.name: agent for agent in agents}
        self.chat_history = []
        self.scene = scene

    def introduce(self):
        pass

    def send(self, sender: CharacterAgent | UserProxyAgent | ConversableAgent,
             recipients: List[CharacterAgent | UserProxyAgent | ConversableAgent],
             content: str, is_resume=False):
        """发送消息：sender -> recipients"""
        if content.split(":")[0] != sender.name:
            content = f"{sender.name}:{content}"
        msg = ConversationRecord(character_id=sender.character_id, name=sender.name, role="user", content=content,
                                 recipient=[recipient.name for recipient in recipients], broadcast=len(recipients) >= 2,
                                 time=int(time.time()), scene_id=self.scene.sid)
        if is_resume is False:
            self.chat_history.append(msg)

        for recipient in recipients:
            # 不要自己与自己对话
            if sender.character_id != recipient.character_id:
                sender.receive(msg.to_dict(), recipient, request_reply=False)
                recipient.receive(msg.to_dict(), sender, request_reply=False)
            # sender.send(msg, recipient, is_resume=is_resume, request_reply=False)

    def reply(self, speaker: ConversableAgent, sender: ConversableAgent, recipients: List[ConversableAgent]):
        """让某个角色生成回复"""
        def process_all_messages_before_reply(messages):
            agent_messages = []
            for agent in self.agents.values():
                agent_messages.extend(speaker.chat_messages[agent]) if agent.name != sender.name else agent_messages
            # 将与要对话的agent的聊天记录放在最后一组
            agent_messages.extend(speaker.chat_messages[sender])
            print(agent_messages)
            return agent_messages

        speaker.register_hook("process_all_messages_before_reply", process_all_messages_before_reply)
        reply = speaker.generate_reply(sender=sender)
        print(f"this is {speaker.name}'s reply: {reply}")

        if reply:
            self.send(sender=speaker, recipients=recipients, content=reply)
        return reply

    def resume_chat(self, chat_messages: List[ConversationRecord]):
        for chat_message in chat_messages:
            self.send(sender=self.agents[chat_message.name],
                      recipients=[self.agents[recipient] for recipient in chat_message.recipient],
                      content=chat_message.content, is_resume=True)


class GroupAgentEngine:
    def __init__(self, ):
        load_dotenv()
        self.config_list = [
            {
                "model": "deepseek-chat",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com",
                "api_type": "openai",  # DeepSeek API 兼容 OpenAI 格式
            }
        ]

        self.llm_config = {
            "config_list": self.config_list,
            # "temperature": 0.7,
        }

    def get_user_character_agent(self, user_character: Character):
        user_character_agent = UserProxyAgent(
            name=user_character.name,
            system_message=user_character.prompt,
            human_input_mode="ALWAYS",
            code_execution_config=False,
            silent=True,
            character_id=user_character.character_id
        )
        return user_character_agent

    def get_character_agent(self, characters: List[Character]):
        character_agent = []
        for character in characters:
            character_agent.append(CharacterAgent(
                name=character.name,
                system_message=character.prompt,
                llm_config=self.llm_config,
                silent=True,
                character_id=character.character_id
            ))
        return character_agent

    def start_conversation(self, scene: Scene,
                           character_agents: List[CharacterAgent | UserProxyAgent],
                           user_agent: UserProxyAgent,
                           speakers: List[CharacterAgent | UserProxyAgent],
                           speak_to: CharacterAgent | UserProxyAgent,
                           speaker_recipients: List[CharacterAgent | UserProxyAgent],
                           chat_history=None,
                           conversation: ConversationRecord = None,
                           recipients: List[CharacterAgent | UserProxyAgent] = None):
        """
        开始对话
        :param scene: 情景类
        :param character_agents: 角色的agent列表, 可以是CharacterAgent或UserProxyAgent
        :param user_agent: 用户的agent, 必须是UserProxyAgent类型
        :param speakers: 指定谁回复, 指定情景中的角色agent, 可以是CharacterAgent或UserProxyAgent, 可多选
        :param speak_to: 指定回复给某个角色agent, 可以是CharacterAgent或UserProxyAgent, 当选择回复该角色时, 聊天历史记录最后一组为与该角色的对话信息
        :param speaker_recipients: 指定谁可以接收到该信息, 可选择多位角色agent, 可以是CharacterAgent或UserProxyAgent
        :param chat_history: 聊天历史记录, 如果有则从该字段中恢复聊天记录
        :param conversation: 用户发送的信息, 可为空, 表示用户不发言, speakers角色发言给speak_to
        :param recipients: 指定哪些角色agent可以接收角色的回复, 可以是CharacterAgent或UserProxyAgent
        :return: List[ConversationRecord]
        """
        # 确保all_agents包含所有可能用到的角色agent
        all_agents = []
        
        # 添加角色列表中的角色agent
        for agent in character_agents:
            if agent not in all_agents:
                all_agents.append(agent)
        
        # 添加发言者
        for agent in speakers:
            if agent not in all_agents:
                all_agents.append(agent)
        
        # 添加被回复的角色
        if speak_to not in all_agents:
            all_agents.append(speak_to)
        
        # 添加接收者
        if recipients:
            for agent in recipients:
                if agent not in all_agents:
                    all_agents.append(agent)
        
        # 添加speaker_recipients
        for agent in speaker_recipients:
            if agent not in all_agents:
                all_agents.append(agent)
        
        # 创建群组聊天, 将用户agent也添加到群组中
        character_group_chat = CharacterGroupChat(all_agents + [user_agent], scene=scene)

        if chat_history:
            character_group_chat.resume_chat(chat_history)

        # 可广播信息
        if conversation and conversation.content and recipients:
            character_group_chat.send(user_agent, recipients, conversation.content)

        # 指定任意角色回复
        for speaker in speakers:
            character_group_chat.reply(speaker=speaker, sender=speak_to, recipients=speaker_recipients)

        return character_group_chat.chat_history


if __name__ == '__main__':
    pass
