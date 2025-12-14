/**
 * 对话管理API接口
 * 使用axios进行HTTP请求
 */

import http from '../utils/request'
import { Conversation } from '@/beans'

class ConversationApi {
  /**
   * 根据角色ID获取对话列表
   */
  async getConversationsByCharacterId(characterId: number): Promise<Conversation[]> {
    const response = await http.get(`/api/conversations/character/${characterId}`)
    return (response as any).map((item: any) => new Conversation(item))
  }

  /**
   * 根据场景ID获取对话列表
   */
  async getConversationsBySceneId(sceneId: string): Promise<Conversation[]> {
    const response = await http.get(`/api/conversations/scene/${sceneId}`)
    return (response as any).map((item: any) => new Conversation(item))
  }

  /**
   * 创建新对话
   */
  async createConversation(data: {
    message: string
    sid: string
    sender_id: number
    role: string
  }): Promise<Conversation> {
    const response = await http.post('/api/conversations', data, {
      timeout: 180000 // 为创建对话设置180秒超时
    })
    return new Conversation(response as any)
  }

  /**
   * 更新对话信息
   */
  async updateConversation(
    conversationId: number,
    data: {
      message: string
      sid: string
      sender_id: number
      role: string
    }
  ): Promise<Conversation> {
    const response = await http.put(`/api/conversations/${conversationId}`, data, {
      timeout: 180000 // 为更新对话设置180秒超时
    })
    return new Conversation(response as any)
  }

  /**
   * 删除对话
   */
  async deleteConversation(conversationId: number): Promise<{ deleted_id: number }> {
    const response = await http.delete(`/api/conversations/${conversationId}`, {
      timeout: 60000 // 为删除对话设置60秒超时
    })
    return response as any
  }
}

// 导出API实例
export const conversationApi = new ConversationApi()
