import os
import json
import time
import autogen
from dotenv import load_dotenv


class InteractiveNovelSystem:
    def __init__(self):
        load_dotenv()
        self.config_list = [
            {
                "model": "deepseek-chat",
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com",
                "api_type": "openai",
            }
        ]

        self.llm_config = {
            "config_list": self.config_list,
            "temperature": 0.7,
            "max_tokens": 500,
        }

        # 故事状态
        self.story_context = {
            "setting": "",
            "story_progress": []
        }

        # 初始化角色
        self.characters = {}
        self.director = None
        self.groupchat = None
        self.manager = None
        self.setup_characters()

    def setup_characters(self):
        """设置角色agents"""

        # 导演（人类代理）
        self.director = autogen.UserProxyAgent(
            name="Director",
            human_input_mode="ALWAYS",
            system_message="""你是故事的导演和旁白，职责：
            1. 设置场景和环境描述
            2. 推动情节发展
            3. 控制故事节奏
            4. 引入转折和新元素
            """,
            code_execution_config=False
        )

        # 主角 - 骑士
        self.characters["Knight"] = autogen.AssistantAgent(
            name="Knight",
            llm_config=self.llm_config,
            system_message="""你是勇敢正直的骑士艾登。
            - 忠诚正直，强烈正义感
            - 武艺高强，但有时冲动
            - 说话直率，骑士风范
            回复时以第一人称，2-3句话。""",
        )

        # 法师
        self.characters["Mage"] = autogen.AssistantAgent(
            name="Mage",
            llm_config=self.llm_config,
            system_message="""你是睿智的法师瑟琳娜。
            - 博学，擅长魔法和古老知识
            - 冷静理性，善于分析
            回复时2-3句话，经常引用智慧或解释现象。""",
        )

        # 游侠
        self.characters["Ranger"] = autogen.AssistantAgent(
            name="Ranger",
            llm_config=self.llm_config,
            system_message="""你是机敏的游侠凯尔。
            - 擅长追踪和射箭，熟悉野外
            - 谨慎但幽默
            回复时2-3句话，经常观察环境并给出实用建议。""",
        )

        # 盗贼
        self.characters["Thief"] = autogen.AssistantAgent(
            name="Thief",
            llm_config=self.llm_config,
            system_message="""你是狡猾的盗贼莉娅。
            - 身手敏捷，擅长开锁和潜行
            - 机智风趣，对朋友忠诚
            回复时2-3句话，经常带幽默感或技能支持。""",
        )

        # 创建群聊
        participants = [self.director] + list(self.characters.values())
        self.groupchat = autogen.GroupChat(
            agents=participants,
            messages=[],
            max_round=20,   # 每个场景最多多少轮对话
        )
        self.manager = autogen.GroupChatManager(groupchat=self.groupchat, llm_config=self.llm_config)

    def start_story(self, initial_setting=""):
        print("=== 🎭 互动小说系统启动（群聊模式） ===")
        self.story_context["setting"] = initial_setting
        print(f"📖 故事背景：{initial_setting}")
        # 导演先发第一条消息
        self.director.initiate_chat(self.manager, message=initial_setting)
        self.manager.run_chat()

    def end_story(self):
        print("\n🎭 故事结束！")
        print("=" * 40)
        for msg in self.groupchat.messages:
            print(f"{msg['role']} ({msg['name']}): {msg['content']}")


def main():
    novel_system = InteractiveNovelSystem()
    initial_setting = input("📖 请描述故事的初始背景: ").strip()
    novel_system.start_story(initial_setting)


if __name__ == "__main__":
    main()
