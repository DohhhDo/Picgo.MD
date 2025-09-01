import axios from 'axios'
import type { AxiosResponse } from 'axios'

// API 基础配置
const API_BASE_URL = 'http://127.0.0.1:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data)
    return Promise.reject(error)
  }
)

// 类型定义
export interface ConversionRequest {
  markdown: string
  quality: number
  output_dir?: string
  use_image_bed?: boolean
  image_bed_provider?: string
  image_bed_config?: Record<string, any>
}

export interface ConversionResponse {
  success: boolean
  message: string
  new_markdown?: string
  stats?: {
    totalOriginalSize: number
    totalConvertedSize: number
    compressionRatio: number
    sizeSaved: number
  }
  task_id?: string
}

export interface TaskStatus {
  status: string
  progress: number
  message: string
  result?: any
}

export interface ImageBedConfig {
  provider: string
  enabled: boolean
  config: Record<string, any>
}

export interface HealthStatus {
  status: string
  conversion_available: boolean
  upload_available: boolean
}

// API 服务类
export class MeowdownAPI {
  // 健康检查
  static async healthCheck(): Promise<HealthStatus> {
    const response: AxiosResponse<HealthStatus> = await apiClient.get('/health')
    return response.data
  }

  // 转换 Markdown
  static async convertMarkdown(request: ConversionRequest): Promise<ConversionResponse> {
    const response: AxiosResponse<ConversionResponse> = await apiClient.post('/api/convert', request)
    return response.data
  }

  // 获取任务状态
  static async getTaskStatus(taskId: string): Promise<TaskStatus> {
    const response: AxiosResponse<TaskStatus> = await apiClient.get(`/api/task/${taskId}`)
    return response.data
  }

  // 上传文件到图床
  static async uploadToImageBed(files: File[], config?: ImageBedConfig): Promise<any> {
    const formData = new FormData()
    
    files.forEach((file) => {
      formData.append('files', file)
    })
    
    if (config) {
      formData.append('config', JSON.stringify(config))
    }

    const response = await apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  }

  // 保存图床配置
  static async saveImageBedConfig(config: ImageBedConfig): Promise<any> {
    const response = await apiClient.post('/api/imagebed/config', config)
    return response.data
  }

  // 获取图床配置
  static async getImageBedConfig(): Promise<ImageBedConfig> {
    const response: AxiosResponse<ImageBedConfig> = await apiClient.get('/api/imagebed/config')
    return response.data
  }

  // 测试图床配置
  static async testImageBedConfig(config: ImageBedConfig): Promise<{ success: boolean; message: string }> {
    const response: AxiosResponse<{ success: boolean; message: string }> = await apiClient.post('/api/imagebed/test', config)
    return response.data
  }
}

// WebSocket 连接管理
export class WebSocketManager {
  private ws: WebSocket | null = null
  private taskId: string
  private onProgress: (progress: number, message: string) => void
  private onComplete: (result: any) => void
  private onError: (error: string) => void

  constructor(
    taskId: string,
    onProgress: (progress: number, message: string) => void,
    onComplete: (result: any) => void,
    onError: (error: string) => void
  ) {
    this.taskId = taskId
    this.onProgress = onProgress
    this.onComplete = onComplete
    this.onError = onError
  }

  connect(): void {
    const wsUrl = `ws://127.0.0.1:8000/ws/${this.taskId}`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected:', this.taskId)
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.completed) {
            this.onComplete(data)
            this.disconnect()
          } else {
            this.onProgress(data.progress, data.message)
          }
        } catch (error) {
          console.error('WebSocket message parse error:', error)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.onError('WebSocket 连接错误')
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected:', this.taskId)
      }
      
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      this.onError('无法连接到服务器')
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export default MeowdownAPI
