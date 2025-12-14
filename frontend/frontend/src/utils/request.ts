/**
 * Axios 配置文件
 * 提供统一的HTTP请求配置、拦截器和错误处理
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import { showError, showSuccess } from './message'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000, // 增加默认超时时间为60秒
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 可以在这里添加token等认证信息
    return config
  },
  (error) => {
    // 请求错误处理
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 统一处理响应数据
    const { data } = response

    // 检查业务状态码
    if (data.code !== 200) {
      const error = new Error(data.message || '操作失败')
      showError(data.message || '操作失败')
      return Promise.reject(error)
    }

    // 显示成功消息（如果有）
    if (data.message) {
      showSuccess(data.message)
    }

    // 返回业务数据
    return data.data
  },
  (error) => {
    // 响应错误处理
    console.error('响应错误:', error)

    let errorMessage = ''

    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status
      errorMessage = error.response.data?.message || `请求失败: ${status}`
    } else if (error.request) {
      // 检查是否是超时错误
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        // 对于LLM相关请求，给出更友好的提示
        errorMessage = '请求超时，LLM可能需要更长时间生成回复，请稍后重试'
      } else {
        // 网络错误
        errorMessage = '网络连接失败，请检查网络设置'
      }
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }

    // 显示错误消息弹窗
    showError(errorMessage)

    return Promise.reject(new Error(errorMessage))
  }
)

// 导出配置好的axios实例
export default request

// 导出常用HTTP方法
export const http = {
  get: request.get,
  post: request.post,
  put: request.put,
  delete: request.delete,
  patch: request.patch,
}
