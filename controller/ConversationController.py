from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from service.ConversationService import ConversationService
from entity.BaseModel import Conversation
from entity.ResponseEntity import ResponseEntity


class CreateConversationRequest(BaseModel):
    """创建对话请求模型"""
    message: str = Field(..., description="对话内容")
    sid: str = Field(..., description="场景ID")
    sender_id: int = Field(..., description="发送者角色ID")
    role: str = Field(..., description="角色类型")


class UpdateConversationRequest(BaseModel):
    """更新对话请求模型"""
    message: str = Field(..., description="对话内容")
    sid: str = Field(..., description="场景ID")
    sender_id: int = Field(..., description="发送者角色ID")
    role: str = Field(..., description="角色类型")


def create_conversation_controller(app: FastAPI, conversation_service: ConversationService):
    """注册对话控制器路由"""

    @app.get("/api/conversations/character/{character_id}")
    async def get_conversations_by_character_id(character_id: int):
        """
        根据角色ID获取对话列表
        """
        try:
            conversations = conversation_service.get_conversations_by_character_id(character_id)

            return ResponseEntity.success(
                data=conversations,
                message="对话列表获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取对话列表失败: {str(e)}"
            )

    @app.get("/api/conversations/scene/{scene_id}")
    async def get_conversations_by_scene_id(scene_id: str):
        """
        根据场景ID获取对话列表
        """
        try:
            conversations = conversation_service.get_conversations_by_scene_id(scene_id)

            return ResponseEntity.success(
                data=conversations,
                message="对话列表获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取对话列表失败: {str(e)}"
            )

    @app.post("/api/conversations")
    async def create_conversation(request: CreateConversationRequest):
        """
        创建新对话
        """
        try:
            conversation = Conversation(
                message=request.message,
                sid=request.sid,
                sender_id=request.sender_id,
                role=request.role
            )

            created_conversation = conversation_service.create_conversation(conversation)

            return ResponseEntity.success(
                data=created_conversation,
                message="对话创建成功"
            )
        except ValueError as e:
            # 参数验证错误
            return ResponseEntity.error(
                code=400,
                message=f"参数错误: {str(e)}"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"创建对话失败: {str(e)}"
            )

    @app.put("/api/conversations/{conversation_id}")
    async def update_conversation(conversation_id: int, request: UpdateConversationRequest):
        """
        更新对话信息
        """
        try:
            conversation = Conversation(
                message=request.message,
                sid=request.sid,
                sender_id=request.sender_id,
                role=request.role
            )

            updated_conversation = conversation_service.update_conversation(conversation_id, conversation)

            if updated_conversation is None:
                return ResponseEntity.not_found(
                    message=f"对话 {conversation_id} 不存在"
                )

            return ResponseEntity.success(
                data=updated_conversation,
                message="对话更新成功"
            )
        except ValueError as e:
            # 参数验证错误
            return ResponseEntity.error(
                code=400,
                message=f"参数错误: {str(e)}"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"更新对话失败: {str(e)}"
            )

    @app.delete("/api/conversations/{conversation_id}")
    async def delete_conversation(conversation_id: int):
        """
        删除对话
        """
        try:
            success = conversation_service.delete_conversation(conversation_id)

            if success:
                return ResponseEntity.success(
                    data=conversation_id,
                    message=f"对话 {conversation_id} 删除成功"
                )
            else:
                return ResponseEntity.not_found(
                    message=f"对话 {conversation_id} 不存在"
                )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"删除对话失败: {str(e)}"
            )
