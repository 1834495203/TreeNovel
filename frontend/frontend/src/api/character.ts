/**
 * 角色管理API接口
 * 使用axios进行HTTP请求
 */

import http from '../utils/request'
import {
  Character,
  CreateCharacterRequest,
  CreateCharacterByNameRequest,
  UpdateCharacterRequest,
} from '@/beans'

class CharacterApi {
  /**
   * 获取所有角色列表
   */
  async getAllCharacters(): Promise<Character[]> {
    const response = await http.get('/api/characters')
    return (response as any).map((item: any) => new Character(item))
  }

  /**
   * 根据ID获取角色信息
   */
  async getCharacterById(characterId: number): Promise<Character> {
    const response = await http.get(`/api/characters/${characterId}`)
    return new Character(response as any)
  }

  /**
   * 创建新角色
   */
  async createCharacter(data: CreateCharacterRequest): Promise<Character> {
    const response = await http.post('/api/characters', data)
    return new Character(response as any)
  }

  /**
   * 根据名称创建角色（使用默认prompt）
   */
  async createCharacterByName(
    data: CreateCharacterByNameRequest
  ): Promise<Character> {
    const response = await http.post('/api/characters/by-conversation', data)
    return new Character(response as any)
  }

  /**
   * 更新角色信息
   */
  async updateCharacter(
    characterId: number,
    data: UpdateCharacterRequest
  ): Promise<Character> {
    const response = await http.put(`/api/characters/${characterId}`, data)
    return new Character(response as any)
  }

  /**
   * 删除角色
   */
  async deleteCharacter(characterId: number): Promise<{ deleted_id: number }> {
    const response = await http.delete(`/api/characters/${characterId}`)
    return response as any
  }

  /**
   * 将角色与情景断连
   */
  async disconnectCharacterFromScene(characterId: number, sceneId: string): Promise<{ character_id: number; scene_id: number }> {
    const response = await http.delete(`/api/characters/${characterId}/scenes/${sceneId}`)
    return response as any
  }
}

// 导出API实例
export const characterApi = new CharacterApi()
