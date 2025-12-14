#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器启动脚本
用于初始化所有依赖并启动FastAPI服务器
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from service.ChatService import ChatService
from service.CharacterService import CharacterService
from service.SceneService import SceneService
from core.chat.LangchainEngine import LangchainEngine
from mapper.ConversationMapper import ConversationMapper
from core.PrepareChatHistory import PrepareChatHistory
from mapper.SceneMapper import SceneMapper
from mapper.CharacterMapper import CharacterMapper
from mapper.CharacterSceneMapper import CharacterSceneMapper
from controller.ChatController import create_chat_controller
from controller.CharacterController import create_character_controller
from controller.SceneController import create_scene_controller
from controller.ConversationController import create_conversation_controller
from service.ConversationService import ConversationService


def init_chat_service() -> ChatService:
    """
    初始化聊天服务
    """
    try:
        # 初始化依赖
        prepare_chat_history = PrepareChatHistory(
            SceneMapper(),
            ConversationMapper(),
            CharacterMapper(),
            CharacterSceneMapper()
        )
        chat_core = LangchainEngine(prepare_chat_history)
        conversation_mapper = ConversationMapper()
        character_mapper = CharacterMapper()
        character_scene_mapper = CharacterSceneMapper()
        scene_mapper = SceneMapper()

        # 创建ChatService实例
        chat_service = ChatService(chat_core, conversation_mapper, character_mapper, character_scene_mapper, scene_mapper)
        return chat_service
    except Exception as e:
        raise Exception(f"初始化ChatService失败: {str(e)}")


def init_character_service() -> CharacterService:
    """
    初始化角色服务
    """
    try:
        # 初始化依赖
        character_mapper = CharacterMapper()

        # 创建CharacterService实例
        character_service = CharacterService(character_mapper)
        return character_service
    except Exception as e:
        raise Exception(f"初始化CharacterService失败: {str(e)}")


def init_scene_service() -> SceneService:
    """
    初始化场景服务
    """
    try:
        # 初始化依赖
        scene_mapper = SceneMapper()
        character_mapper = CharacterMapper()
        character_scene_mapper = CharacterSceneMapper()

        # 创建SceneService实例
        scene_service = SceneService(
            scene_mapper=scene_mapper,
            character_mapper=character_mapper,
            character_scene_mapper=character_scene_mapper
        )
        return scene_service
    except Exception as e:
        raise Exception(f"初始化SceneService失败: {str(e)}")


def init_conversation_service() -> ConversationService:
    """
    初始化对话服务
    """
    try:
        # 初始化依赖
        conversation_mapper = ConversationMapper()

        # 创建ConversationService实例
        conversation_service = ConversationService(conversation_mapper)
        return conversation_service
    except Exception as e:
        raise Exception(f"初始化ConversationService失败: {str(e)}")


def create_app() -> FastAPI:
    """
    创建并配置FastAPI应用
    """
    # 创建FastAPI应用实例
    app = FastAPI(
        title="ReactNovel API",
        description="基于FastAPI的角色扮演聊天API服务，支持场景管理和角色管理",
        version="1.0.0"
    )

    # 添加CORS中间件，支持跨域请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vue开发服务器
            "http://127.0.0.1:5173",  # Vue开发服务器
            "http://localhost:5174",  # 其他常见前端端口
            "http://127.0.0.1:5174",
        ],
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有HTTP头
    )

    # 初始化服务
    chat_service = init_chat_service()
    character_service = init_character_service()
    scene_service = init_scene_service()
    conversation_service = init_conversation_service()

    # 注册控制器路由
    create_chat_controller(app, chat_service)
    create_character_controller(app, character_service)
    create_scene_controller(app, scene_service)
    create_conversation_controller(app, conversation_service)

    return app


def main():
    """
    主函数：启动服务器
    """
    # 创建应用
    app = create_app()

    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False  # 生产环境建议设置为False
    )


if __name__ == "__main__":
    main()
