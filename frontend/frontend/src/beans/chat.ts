/**
 * 对话和聊天相关的Bean类型定义
 */

/**
 * 对话实体
 */
export class Conversation {
  message!: string
  sid!: string
  sender_id!: number
  role!: string
  conversation_id?: number

  constructor(data: Partial<Conversation>) {
    Object.assign(this, data)
  }
}

/**
 * 聊天请求
 */
export class ChatRequest {
  roleplay_id!: number
  conversation!: Conversation
  stream!: boolean

  constructor(data: Partial<ChatRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 聊天响应 - ResponseEntity格式
 */
export class ChatResponse {
  code!: number
  message!: string
  data?: {
    response?: string
    user_conversation_id?: number
    assistant_conversation_id?: number
    roleplay_id?: number
    timestamp?: number
  }

  constructor(data: Partial<ChatResponse>) {
    Object.assign(this, data)
  }
}
