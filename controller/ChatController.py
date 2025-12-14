from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import json

from service.ChatService import ChatService
from entity.BaseModel import Conversation, Character
from entity.ResponseEntity import ResponseEntity
from utils.ConvertPydantic import dataclass_to_pydantic

# 聊天消息模型
ConversationRequest = dataclass_to_pydantic(Conversation)


class ChatRequest(BaseModel):
    """聊天请求模型"""
    roleplay_id: int = Field(..., description="LLM扮演的角色ID")
    conversation: ConversationRequest = Field(..., description="对话内容")
    stream: bool = Field(default=False, description="是否流式返回响应")


def create_chat_controller(app: FastAPI, chat_service: ChatService):
    """注册聊天控制器路由"""

    @app.post("/api/chat")
    async def chat(request: ChatRequest):
        """
        处理聊天请求
        """
        try:
            # 转换请求模型为内部Conversation模型
            conversation = Conversation(
                message=request.conversation.message,
                sid=request.conversation.sid,
                sender_id=request.conversation.sender_id,
                role=request.conversation.role
            )

            # 调用ChatService的chat方法
            result = chat_service.chat(
                roleplay_id=request.roleplay_id,
                conversation=conversation,
                stream=request.stream
            )

            if request.stream:
                # 流式响应需要特殊处理
                if "error" in result:
                    # 错误处理
                    return {"stream_data": True, "type": "error", "error": result["error"]}
                else:
                    # 返回流式数据和conversation_id
                    return {
                        "stream_data": True,
                        "type": "streaming",
                        "user_conversation_id": result.get("user_conversation_id"),
                        "assistant_conversation_id": result.get("assistant_conversation_id"),
                        "stream": result.get("stream")
                    }
            else:
                # 非流式响应 - 使用ResponseEntity
                if "error" in result:
                    return ResponseEntity.error(
                        code=500,
                        message=result["error"]
                    )
                else:
                    return ResponseEntity.success(
                        data={
                            "response": result.get("response"),
                            "user_conversation_id": result.get("user_conversation_id"),
                            "assistant_conversation_id": result.get("assistant_conversation_id"),
                            "roleplay_id": request.roleplay_id,
                            "timestamp": int(__import__('time').time())
                        },
                        message="对话生成成功"
                    )

        except ValueError as e:
            # 参数错误
            return ResponseEntity.error(
                code=400,
                message=f"参数错误: {str(e)}"
            )
        except PermissionError:
            # 权限错误
            return ResponseEntity.unauthorized(
                message="权限不足"
            )
        except Exception as e:
            # 其他错误
            return ResponseEntity.error(
                code=500,
                message=f"聊天处理失败: {str(e)}"
            )

    @app.post("/api/chat/stream")
    async def chat_stream(request: ChatRequest):
        """
        处理流式聊天请求，使用Server-Sent Events (SSE)
        """
        try:
            # 转换请求模型为内部Conversation模型
            conversation = Conversation(
                message=request.conversation.message,
                sid=request.conversation.sid,
                sender_id=request.conversation.sender_id,
                role=request.conversation.role
            )

            # 调用ChatService的chat方法，强制流式响应
            result = chat_service.chat(
                roleplay_id=request.roleplay_id,
                conversation=conversation,
                stream=True
            )

            # 提取conversation_id
            user_conversation_id = result.get("user_conversation_id")
            assistant_conversation_id = result.get("assistant_conversation_id")

            # 定义SSE生成器函数
            def sse_generator():
                try:
                    if "error" in result:
                        # 发送错误信息
                        error_data = {
                            "error": {
                                "message": result["error"]
                            }
                        }
                        yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                        return

                    # 首先发送conversation_id信息
                    id_info_data = {
                        "type": "ids",
                        "user_conversation_id": user_conversation_id,
                        "assistant_conversation_id": assistant_conversation_id
                    }
                    yield f"data: {json.dumps(id_info_data, ensure_ascii=False)}\n\n"

                    # 发送流式内容
                    for chunk in result.get("stream", []):
                        # 将每个chunk包装成SSE格式
                        sse_data = {
                            "data": {
                                "content": str(chunk)
                            }
                        }
                        yield f"data: {json.dumps(sse_data, ensure_ascii=False)}\n\n"

                    # 发送结束标识
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    # 发送错误信息
                    error_data = {
                        "error": {
                            "message": f"流式响应错误: {str(e)}"
                        }
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

            # 返回StreamingResponse，使用SSE格式
            return StreamingResponse(
                sse_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # 禁用nginx缓冲
                }
            )

        except ValueError as e:
            # 参数错误
            return ResponseEntity.error(
                code=400,
                message=f"参数错误: {str(e)}"
            )
        except PermissionError:
            # 权限错误
            return ResponseEntity.unauthorized(
                message="权限不足"
            )
        except Exception as e:
            # 其他错误
            return ResponseEntity.error(
                code=500,
                message=f"流式聊天处理失败: {str(e)}"
            )

    @app.get("/api/health")
    async def health_check(chat_service: ChatService = Depends(lambda: chat_service)):
        """健康检查接口"""
        return ResponseEntity.success(
            data={
                "status": "healthy",
                "service": "Chat API",
                "chat_service_available": chat_service is not None
            },
            message="服务运行正常"
        )
