from fastapi import FastAPI
from pydantic import BaseModel, Field

from service.CharacterService import CharacterService
from entity.BaseModel import Character
from entity.ResponseEntity import ResponseEntity


class CreateCharacterRequest(BaseModel):
    """创建角色请求模型"""
    name: str = Field(..., description="角色名称")
    prompt: str = Field(..., description="角色设定prompt")
    is_visible: bool = Field(default=True, description="角色是否可见")


class UpdateCharacterRequest(BaseModel):
    """更新角色请求模型"""
    name: str = Field(..., description="角色名称")
    prompt: str = Field(..., description="角色设定prompt")
    is_visible: bool = Field(default=True, description="角色是否可见")


class CreateCharacterByNameRequest(BaseModel):
    """根据名称创建角色请求模型"""
    name: str = Field(..., description="角色名称")
    prompt: str = Field(default="这是一个默认角色", description="角色设定prompt")
    is_visible: bool = Field(default=True, description="角色是否可见")


def create_character_controller(app: FastAPI, character_service: CharacterService):
    """注册角色控制器路由"""

    @app.get("/api/characters")
    async def get_all_characters():
        """
        获取所有角色列表
        """
        try:
            characters = character_service.get_all_characters()

            return ResponseEntity.success(
                data=characters,
                message="角色列表获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取角色列表失败: {str(e)}"
            )

    @app.get("/api/characters/{character_id}")
    async def get_character_by_id(character_id: int):
        """
        根据ID获取角色信息
        """
        try:
            character = character_service.get_character_by_id(character_id)

            if character is None:
                return ResponseEntity.not_found(
                    message=f"角色 {character_id} 不存在"
                )

            return ResponseEntity.success(
                data=character,
                message="角色信息获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取角色信息失败: {str(e)}"
            )

    @app.post("/api/characters")
    async def create_character(request: CreateCharacterRequest):
        """
        创建新角色
        """
        try:
            character = Character(
                name=request.name,
                prompt=request.prompt,
                is_visible=request.is_visible
            )

            created_character = character_service.create_character(character)

            return ResponseEntity.success(
                data=created_character,
                message="角色创建成功"
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
                message=f"创建角色失败: {str(e)}"
            )

    @app.post("/api/characters/by-conversation")
    async def create_character_by_conversation(request: CreateCharacterByNameRequest):
        """
        根据名称创建角色（使用默认prompt）
        """
        try:
            character = character_service.create_character(
                Character(name=request.name, prompt=request.prompt, is_visible=request.is_visible)
            )

            return ResponseEntity.success(
                data=character,
                message="角色创建成功"
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
                message=f"创建角色失败: {str(e)}"
            )

    @app.put("/api/characters/{character_id}")
    async def update_character(character_id: int, request: UpdateCharacterRequest):
        """
        更新角色信息
        """
        try:
            character = Character(
                name=request.name,
                prompt=request.prompt,
                is_visible=request.is_visible
            )

            updated_character = character_service.update_character(character_id, character)

            if updated_character is None:
                return ResponseEntity.not_found(
                    message=f"角色 {character_id} 不存在"
                )

            return ResponseEntity.success(
                data=updated_character,
                message="角色更新成功"
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
                message=f"更新角色失败: {str(e)}"
            )

    @app.delete("/api/characters/{character_id}")
    async def delete_character(character_id: int):
        """
        删除角色
        """
        try:
            success = character_service.delete_character(character_id)

            if success:
                return ResponseEntity.success(
                    data=character_id,
                    message=f"角色 {character_id} 删除成功"
                )
            else:
                return ResponseEntity.not_found(
                    message=f"角色 {character_id} 不存在"
                )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"删除角色失败: {str(e)}"
            )

    @app.delete("/api/characters/{character_id}/scenes/{scene_id}")
    async def disconnect_character_from_scene(character_id: int, scene_id: str):
        """
        删除角色与场景的关联
        """
        try:
            success = character_service.disconnect_character_from_scene(character_id, scene_id)

            if success:
                return ResponseEntity.success(
                    data={"character_id": character_id, "scene_id": scene_id},
                    message=f"角色 {character_id} 与场景 {scene_id} 的关联已删除"
                )
            else:
                return ResponseEntity.not_found(
                    message=f"角色 {character_id} 与场景 {scene_id} 的关联不存在"
                )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"删除角色与场景关联失败: {str(e)}"
            )
