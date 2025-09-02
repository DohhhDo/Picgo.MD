import { useState, useCallback, useEffect } from 'react'
import { MeowdownAPI } from '../services/api'
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


  // 检查后端连接状态
  const checkConnection = useCallback(async () => {
    try {
      await MeowdownAPI.healthCheck()
      setState(prev => ({
        ...prev,
        isConnected: true,
        error: null,
      }))
      return true
    } catch (error) {
      // 不再回退 axios，直接提示未连接
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
      // 发送转换请求（后端会在完成后才返回，因此直接以返回结果为准更新状态）
      const response = await MeowdownAPI.convertMarkdown(request)

      if (response.success) {
        setState(prev => ({
          ...prev,
          isConverting: false,
          progress: 100,
          progressMessage: '转换完成！',
          lastResult: response,
        }))
        // 如需实时进度，需服务端先返回 task_id 后异步处理；当前实现为同步返回，故不再依赖 WS。
        return response
      }

      throw new Error(response.message || '转换请求失败')
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
    setState(initialState)
  }, [])

  // 组件挂载时检查连接
  useEffect(() => {
    checkConnection()
    
    // 定期检查连接状态
    const interval = setInterval(checkConnection, 10000)
    
    return () => {
      clearInterval(interval)
    }
  }, [checkConnection])

  return {
    state,
    checkConnection,
    startConversion,
    resetState,
  }
}
