import { useState, useCallback, useEffect } from 'react'
import { MeowdownAPI, WebSocketManager } from '../services/api'
import type { ConversionRequest, ConversionResponse } from '../services/api'

interface ApiState {
  isConnected: boolean
  isConverting: boolean
  progress: number
  progressMessage: string
  lastResult: ConversionResponse | null
  error: string | null
}

const initialState: ApiState = {
  isConnected: false,
  isConverting: false,
  progress: 0,
  progressMessage: '准备就绪',
  lastResult: null,
  error: null,
}

export const useApiState = () => {
  const [state, setState] = useState<ApiState>(initialState)
  const [wsManager, setWsManager] = useState<WebSocketManager | null>(null)

  // 检查后端连接状态
  const checkConnection = useCallback(async () => {
    try {
      const health = await MeowdownAPI.healthCheck()
      setState(prev => ({
        ...prev,
        isConnected: health.status === 'healthy',
        error: null,
      }))
      return health.status === 'healthy'
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConnected: false,
        error: '无法连接到后端服务',
      }))
      return false
    }
  }, [])

  // 启动转换
  const startConversion = useCallback(async (request: ConversionRequest) => {
    setState(prev => ({
      ...prev,
      isConverting: true,
      progress: 0,
      progressMessage: '开始转换...',
      error: null,
    }))

    try {
      // 发送转换请求
      const response = await MeowdownAPI.convertMarkdown(request)
      
      if (response.success && response.task_id) {
        // 创建 WebSocket 连接监听进度
        const manager = new WebSocketManager(
          response.task_id,
          // onProgress
          (progress: number, message: string) => {
            setState(prev => ({
              ...prev,
              progress,
              progressMessage: message,
            }))
          },
          // onComplete
          (result: any) => {
            setState(prev => ({
              ...prev,
              isConverting: false,
              progress: 100,
              progressMessage: '转换完成！',
              lastResult: response,
            }))
            setWsManager(null)
          },
          // onError
          (error: string) => {
            setState(prev => ({
              ...prev,
              isConverting: false,
              error,
              progressMessage: '转换失败',
            }))
            setWsManager(null)
          }
        )

        manager.connect()
        setWsManager(manager)
        
        return response
      } else {
        throw new Error(response.message || '转换请求失败')
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        isConverting: false,
        error: error instanceof Error ? error.message : '转换失败',
        progressMessage: '转换失败',
      }))
      throw error
    }
  }, [])

  // 重置状态
  const resetState = useCallback(() => {
    if (wsManager) {
      wsManager.disconnect()
      setWsManager(null)
    }
    setState(initialState)
  }, [wsManager])

  // 组件挂载时检查连接
  useEffect(() => {
    checkConnection()
    
    // 定期检查连接状态
    const interval = setInterval(checkConnection, 10000)
    
    return () => {
      clearInterval(interval)
      if (wsManager) {
        wsManager.disconnect()
      }
    }
  }, [checkConnection, wsManager])

  return {
    state,
    checkConnection,
    startConversion,
    resetState,
  }
}
