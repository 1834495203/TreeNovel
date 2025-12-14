/**
 * 聊天API接口
 * 使用axios进行HTTP请求
 */

import http from '../utils/request'
import { ChatRequest, ChatResponse } from '@/beans'

// 提取baseURL常量，避免硬编码
const BASE_URL = 'http://localhost:8000'

class ChatApi {
  /**
   * 发送聊天消息
   */
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    const response = await http.post('/api/chat', data, {
      timeout: 180000 // 为LLM请求设置180秒超时（3分钟）
    })
    return new ChatResponse(response as any)
  }

  /**
   * 发送流式聊天消息
   */
  async sendMessageStream(data: ChatRequest): Promise<AsyncIterable<any>> {
    // 使用BASE_URL常量构建完整URL
    const response = await fetch(`${BASE_URL}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(data)
    })

    if (!response.body) {
      throw new Error('响应体为空')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    async function* generate() {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6)
              if (jsonStr === '[DONE]') {
                return
              }
              yield JSON.parse(jsonStr)
            } catch (e) {
              console.error('解析流式数据失败:', e)
            }
          }
        }
      }
    }

    return generate()
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<any> {
    const response = await http.get('/api/health')
    return response as any
  }
}

// 导出API实例
export const chatApi = new ChatApi()
