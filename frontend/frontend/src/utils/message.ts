import { createApp, ref, h } from 'vue'
import MessageDialog from '@/components/MessageDialog.vue'

interface MessageOptions {
  type?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  duration?: number
  showClose?: boolean
  closeOnOverlay?: boolean
}

// 使用ref来跟踪当前显示的消息
const currentMessage = ref<{
  visible: boolean
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  title?: string
  duration: number
  showClose: boolean
  closeOnOverlay: boolean
} | null>(null)

// 创建Vue应用实例用于挂载MessageDialog
let app: ReturnType<typeof createApp> | null = null

/**
 * 显示消息弹窗
 * @param message 消息内容
 * @param options 配置选项
 */
export const showMessage = (message: string, options: MessageOptions = {}) => {
  // 如果已有消息在显示，先关闭它
  if (currentMessage.value?.visible) {
    currentMessage.value.visible = false
  }

  // 设置新消息
  currentMessage.value = {
    visible: true,
    type: options.type || 'info',
    message,
    title: options.title,
    duration: options.duration ?? 3000,
    showClose: options.showClose ?? true,
    closeOnOverlay: options.closeOnOverlay ?? true
  }

  // 如果应用实例不存在，创建一个
  if (!app) {
    app = createApp({
      render() {
        return h(MessageDialog, {
          type: currentMessage.value?.type,
          message: currentMessage.value?.message || '',
          title: currentMessage.value?.title,
          duration: currentMessage.value?.duration,
          showClose: currentMessage.value?.showClose,
          closeOnOverlay: currentMessage.value?.closeOnOverlay,
          'onClose': () => {
            if (currentMessage.value) {
              currentMessage.value.visible = false
            }
          }
        })
      }
    })

    // 挂载到body
    const mountNode = document.createElement('div')
    document.body.appendChild(mountNode)
    app.mount(mountNode)
  } else {
    // 更新应用实例
    app._instance?.proxy?.$forceUpdate()
  }
}

/**
 * 显示成功消息
 * @param message 消息内容
 * @param options 配置选项
 */
export const showSuccess = (message: string, options: Omit<MessageOptions, 'type'> = {}) => {
  showMessage(message, { ...options, type: 'success' })
}

/**
 * 显示错误消息
 * @param message 消息内容
 * @param options 配置选项
 */
export const showError = (message: string, options: Omit<MessageOptions, 'type'> = {}) => {
  showMessage(message, { ...options, type: 'error' })
}

/**
 * 显示警告消息
 * @param message 消息内容
 * @param options 配置选项
 */
export const showWarning = (message: string, options: Omit<MessageOptions, 'type'> = {}) => {
  showMessage(message, { ...options, type: 'warning' })
}

/**
 * 显示信息消息
 * @param message 消息内容
 * @param options 配置选项
 */
export const showInfo = (message: string, options: Omit<MessageOptions, 'type'> = {}) => {
  showMessage(message, { ...options, type: 'info' })
}
