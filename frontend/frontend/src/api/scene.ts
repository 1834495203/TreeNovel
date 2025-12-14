/**
 * 场景管理API接口
 * 使用axios进行HTTP请求
 */

import http from '../utils/request'
import {
  Scene,
  CreateSceneByCurrentRequest,
  UpdateSceneRequest,
  ConnectCharacterRequest,
  SceneGraph,
  Character,
  CharacterSceneDto,
} from '@/beans'

class SceneApi {
  /**
   * 获取所有场景列表
   */
  async getAllScenes(): Promise<Scene[]> {
    const response = await http.get('/api/scenes')
    return (response as any).map((item: any) => new Scene(item))
  }

  /**
   * 根据ID获取场景信息
   */
  async getSceneById(sceneId: string): Promise<Scene> {
    const response = await http.get(`/api/scenes/${sceneId}`)
    return new Scene(response as any)
  }

  /**
   * 创建新场景
   */
  async createScene(data: CreateSceneByCurrentRequest): Promise<Scene> {
    const response = await http.post('/api/scenes', data)
    return new Scene(response as any)
  }

  /**
   * 更新场景信息
   */
  async updateScene(sceneId: string, data: UpdateSceneRequest): Promise<Scene> {
    const response = await http.put(`/api/scenes/${sceneId}`, data)
    return new Scene(response as any)
  }

  /**
   * 删除场景
   */
  async deleteScene(sceneId: string): Promise<{ deleted_id: string }> {
    const response = await http.delete(`/api/scenes/${sceneId}`)
    return response as any
  }

  /**
   * 获取场景的角色列表
   */
  async getSceneCharacters(sceneId: string): Promise<CharacterSceneDto[]> {
    const response: CharacterSceneDto[] = await http.get(`/api/scenes/${sceneId}/characters`)
    return response as CharacterSceneDto[]
  }

  /**
   * 连接角色到场景
   */
  async connectCharacterToScene(
    sceneId: string,
    data: ConnectCharacterRequest
  ): Promise<any> {
    const response = await http.post(`/api/scenes/${sceneId}/characters`, data)
    return response as any
  }

  /**
   * 获取场景关系图
   */
  async getScenesGraph(): Promise<SceneGraph> {
    const response = await http.get('/api/scenes/graph')
    return new SceneGraph(response as any)
  }

  /**
   * 获取场景的父场景链
   */
  async getSceneParents(sceneId: string): Promise<any[][]> {
    const response = await http.get(`/api/scenes/${sceneId}/parents`)
    return response as any
  }
}

// 导出API实例
export const sceneApi = new SceneApi()
