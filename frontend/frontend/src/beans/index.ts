/**
 * 统一的Bean类型定义导出
 * 按业务模块拆分，便于维护和管理
 */

// 角色相关Bean
export * from './character'

// 场景相关Bean
export * from './scene'

// 对话和聊天相关Bean
export * from './chat'

// 基础响应实体格式
export interface ResponseEntity<T = any> {
  code: number
  message: string
  data: T | null
}
