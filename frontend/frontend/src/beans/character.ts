/**
 * 角色相关的Bean类型定义
 */

/**
 * 角色实体
 */
export class Character {
  character_id!: number
  name!: string
  prompt!: string
  is_visible!: boolean

  constructor(data: Partial<Character>) {
    Object.assign(this, data)
  }
}

/**
 * 创建角色请求
 */
export class CreateCharacterRequest {
  name!: string
  prompt!: string
  is_visible!: boolean

  constructor(data: Partial<CreateCharacterRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 根据名称创建角色请求
 */
export class CreateCharacterByNameRequest {
  name!: string
  prompt?: string
  is_visible!: boolean

  constructor(data: Partial<CreateCharacterByNameRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 更新角色请求
 */
export class UpdateCharacterRequest {
  name?: string
  prompt?: string
  is_visible?: boolean

  constructor(data: Partial<UpdateCharacterRequest>) {
    Object.assign(this, data)
  }
}
