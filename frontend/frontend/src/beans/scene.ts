/**
 * 场景相关的Bean类型定义
 */

import type { Character } from "./character"

/**
 * 场景实体
 */
export class Scene {
  sid!: string
  name!: string
  is_main!: boolean
  summary!: string
  is_root!: boolean

  constructor(data: Partial<Scene>) {
    Object.assign(this, data)
  }
}

/**
 * 创建场景请求
 */
export class CreateSceneRequest {
  sid!: string
  name!: string
  is_main!: boolean
  summary!: string
  is_root!: boolean

  constructor(data: Partial<CreateSceneRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 基于当前场景创建请求
 */
export class CreateSceneByCurrentRequest {
  new_scene!: CreateSceneRequest
  current_scenes_id?: string | string[]
  character_ids?: number[]

  constructor(data: Partial<CreateSceneByCurrentRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 更新场景请求
 */
export class UpdateSceneRequest {
  name?: string
  is_main?: boolean
  summary?: string
  is_root?: boolean

  constructor(data: Partial<UpdateSceneRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 连接角色到场景请求
 */
export class ConnectCharacterRequest {
  character_id!: number
  sort_order?: number
  is_visible?: boolean

  constructor(data: Partial<ConnectCharacterRequest>) {
    Object.assign(this, data)
  }
}

/**
 * 场景关系边
 */
export class SceneEdge {
  source!: string
  target!: string

  constructor(data: Partial<SceneEdge>) {
    Object.assign(this, data)
  }
}

/**
 * 场景图
 */
export class SceneGraph {
  nodes!: Scene[]
  edges!: SceneEdge[]

  constructor(data: Partial<SceneGraph>) {
    Object.assign(this, data)
  }
}


export class CharacterSceneDto {
  character_id!: number
  sid!: string
  sort_order!: number
  is_visible!: boolean
  parent_id?: number
  id?: number
  character!: Character
}
