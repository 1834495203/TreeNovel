import uuid
from typing import List, Optional, Union
from fastapi import FastAPI

from config.Logger import logger
from service.SceneService import SceneService
from entity.Scene import Scene
from entity.ResponseEntity import ResponseEntity
from pydantic import BaseModel, Field


# 创建场景请求模型
class CreateSceneRequest(BaseModel):
    """创建场景请求模型"""
    sid: str = Field(..., description="场景ID")
    name: str = Field(..., description="场景名称")
    is_main: bool = Field(..., description="是否为主场景")
    summary: str = Field(..., description="场景摘要")
    is_root: bool = Field(..., description="是否为根场景")


# 基于当前场景创建请求模型
class CreateSceneByCurrentRequest(BaseModel):
    """基于当前场景创建新场景请求模型"""
    new_scene: CreateSceneRequest = Field(..., description="新场景信息")
    current_scenes_id: Optional[Union[str, List[str]]] = Field(None, description="当前场景ID列表或单个场景ID")
    character_ids: Optional[List[int]] = Field(None, description="角色ID列表，为空则继承当前场景的角色列表")


# 更新场景请求模型
class UpdateSceneRequest(BaseModel):
    """更新场景请求模型"""
    name: Optional[str] = Field(None, description="场景名称")
    is_main: Optional[bool] = Field(None, description="是否为主场景")
    summary: Optional[str] = Field(None, description="场景摘要")
    is_root: Optional[bool] = Field(None, description="是否为根场景")


# 连接角色到场景请求模型
class ConnectCharacterRequest(BaseModel):
    """连接角色到场景请求模型"""
    character_id: int = Field(..., description="角色ID")
    sort_order: int = Field(default=0, description="角色排序")
    is_visible: bool = Field(default=True, description="角色是否可见")


def create_scene_controller(app: FastAPI, scene_service: SceneService):
    """注册场景控制器路由"""

    @app.get("/api/scenes")
    async def get_all_scenes():
        """
        获取所有场景列表
        """
        try:
            # 从图中获取所有场景
            graph = scene_service.get_all_scenes_graph()
            scene_list = [
                {
                    "sid": scene.sid,
                    "name": scene.name,
                    "is_main": scene.is_main,
                    "summary": scene.summary,
                    "is_root": scene.is_root
                }
                for scene in graph.nodes
            ]
            return ResponseEntity.success(
                data=scene_list,
                message="场景列表获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取场景列表失败: {str(e)}"
            )

    @app.get("/api/scenes/graph")
    async def get_scenes_graph():
        """
        获取场景关系图
        """
        try:
            graph = scene_service.get_all_scenes_graph()

            return ResponseEntity.success(
                data=graph,
                message="场景图获取成功"
            )
        except Exception as e:
            logger.error(f"获取场景图失败: {str(e)}")
            return ResponseEntity.error(
                code=500,
                message=f"获取场景图失败: {str(e)}"
            )

    @app.get("/api/scenes/{scene_id}")
    async def get_scene_by_id(scene_id: str):
        """
        根据ID获取场景信息
        """
        try:
            scene = scene_service.get_scene_by_id(scene_id)

            if scene is None:
                return ResponseEntity.not_found(
                    message=f"场景 {scene_id} 不存在"
                )

            return ResponseEntity.success(
                data={
                    "sid": scene.sid,
                    "name": scene.name,
                    "is_main": scene.is_main,
                    "summary": scene.summary,
                    "is_root": scene.is_root
                },
                message="场景信息获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取场景信息失败: {str(e)}"
            )

    @app.post("/api/scenes")
    async def create_scene(request: CreateSceneByCurrentRequest):
        """
        创建新场景（基于当前场景或全新创建）
        """
        try:
            if request.new_scene.sid is None or request.new_scene.sid == "":
                request.new_scene.sid = str(uuid.uuid4())

            # 转换请求模型为内部Scene模型
            new_scene = Scene(
                sid=request.new_scene.sid,
                name=request.new_scene.name,
                is_main=request.new_scene.is_main,
                summary=request.new_scene.summary,
                is_root=request.new_scene.is_root
            )

            # 创建场景
            created_scene = scene_service.create_scene_by_current_scene(
                new_scene=new_scene,
                current_scenes_id=request.current_scenes_id,
                character_ids=request.character_ids
            )

            return ResponseEntity.success(
                data={
                    "sid": created_scene.sid,
                    "name": created_scene.name,
                    "is_main": created_scene.is_main,
                    "summary": created_scene.summary,
                    "is_root": created_scene.is_root
                },
                message="场景创建成功"
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
                message=f"创建场景失败: {str(e)}"
            )

    @app.put("/api/scenes/{scene_id}")
    async def update_scene(scene_id: str, request: UpdateSceneRequest):
        """
        更新场景信息
        """
        try:
            # 构建更新后的Scene对象，只更新提供的字段
            current_scene = scene_service.get_scene_by_id(scene_id)
            if current_scene is None:
                return ResponseEntity.not_found(
                    message=f"场景 {scene_id} 不存在"
                )

            # 更新字段（只更新非None的字段）
            updated_scene = Scene(
                sid=scene_id,
                name=request.name if request.name is not None else current_scene.name,
                is_main=request.is_main if request.is_main is not None else current_scene.is_main,
                summary=request.summary if request.summary is not None else current_scene.summary,
                is_root=request.is_root if request.is_root is not None else current_scene.is_root
            )

            result = scene_service.update_scene_by_id(scene_id, updated_scene)

            return ResponseEntity.success(
                data={
                    "sid": result.sid,
                    "name": result.name,
                    "is_main": result.is_main,
                    "summary": result.summary,
                    "is_root": result.is_root
                },
                message="场景更新成功"
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
                message=f"更新场景失败: {str(e)}"
            )

    @app.delete("/api/scenes/{scene_id}")
    async def delete_scene(scene_id: str):
        """
        删除场景
        """
        try:
            success = scene_service.delete_scene_by_id(scene_id)

            if success:
                return ResponseEntity.success(
                    data={"deleted_id": scene_id},
                    message=f"场景 {scene_id} 删除成功"
                )
            else:
                return ResponseEntity.not_found(
                    message=f"场景 {scene_id} 不存在"
                )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"删除场景失败: {str(e)}"
            )

    @app.get("/api/scenes/{scene_id}/characters")
    async def get_scene_characters(scene_id: str, include_invisible: bool = True):
        """
        获取场景的角色列表
        """
        try:
            character_scene_dtos = scene_service.get_characters_by_scene(scene_id, include_invisible=include_invisible)

            # 转换为响应格式，包含完整的角色信息和关联信息
            character_list = [
                {
                    "character_id": dto.character_id,
                    "scene_id": dto.sid,
                    "sort_order": dto.sort_order,
                    "is_visible": dto.is_visible,
                    "parent_id": dto.parent_id,
                    "character_scene_id": dto.character_scene_id,
                    "character": {
                        "character_id": dto.character.character_id,
                        "name": dto.character.name,
                        "prompt": dto.character.prompt,
                        "is_visible": dto.character.is_visible
                    }
                }
                for dto in character_scene_dtos
            ]

            return ResponseEntity.success(
                data=character_list,
                message="场景角色列表获取成功"
            )
        except Exception as e:
            logger.error(f"获取场景角色列表失败: {str(e)}")
            return ResponseEntity.error(
                code=500,
                message=f"获取场景角色列表失败: {str(e)}"
            )

    @app.post("/api/scenes/{scene_id}/characters")
    async def connect_character_to_scene(scene_id: str, request: ConnectCharacterRequest):
        """
        连接角色到场景
        """
        try:
            # 验证场景是否存在
            scene = scene_service.get_scene_by_id(scene_id)
            if scene is None:
                return ResponseEntity.not_found(
                    message=f"场景 {scene_id} 不存在"
                )

            success = scene_service.connect_character_2_scene(
                character_id=request.character_id,
                scene_id=scene_id,
                sort_order=request.sort_order,
                is_visible=request.is_visible
            )

            if success:
                return ResponseEntity.success(
                    data={
                        "scene_id": scene_id,
                        "character_id": request.character_id,
                        "sort_order": request.sort_order,
                        "is_visible": request.is_visible
                    },
                    message="角色连接场景成功"
                )
            else:
                return ResponseEntity.error(
                    code=500,
                    message="角色连接场景失败"
                )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"连接角色到场景失败: {str(e)}"
            )

    @app.get("/api/scenes/{scene_id}/parents")
    async def get_scene_parents(scene_id: str):
        """
        获取场景的所有父场景链
        """
        try:
            all_parents = scene_service.get_all_parents_by_id(scene_id)

            # 转换父场景链为字典格式
            parent_chains = []
            for parent_chain in all_parents:
                chain = [
                    {
                        "sid": scene.sid,
                        "name": scene.name,
                        "is_main": scene.is_main,
                        "summary": scene.summary,
                        "is_root": scene.is_root
                    }
                    for scene in parent_chain
                ]
                parent_chains.append(chain)

            return ResponseEntity.success(
                data=parent_chains,
                message="场景父场景链获取成功"
            )
        except Exception as e:
            return ResponseEntity.error(
                code=500,
                message=f"获取场景父场景链失败: {str(e)}"
            )
