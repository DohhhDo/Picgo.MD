// HTTP请求处理 - 支持Web和Tauri环境
import { getApiBaseUrl } from './config'

// 检测是否在Tauri环境中
const isTauriEnvironment = typeof window !== 'undefined' && (window as any).__TAURI__

// Tauri invoke函数（仅在Tauri环境中可用）
let tauriInvoke: ((cmd: string, args?: any) => Promise<any>) | null = null

// 如果在Tauri环境中，设置invoke函数
if (isTauriEnvironment) {
  // 这个会在运行时动态设置，编译时不会报错
  tauriInvoke = (window as any).__TAURI__.invoke
}

// 响应接口定义
export interface ConversionResponse {
  success: boolean
  message: string
  new_markdown?: string
  stats?: {
    total_images: number
    converted_images: number
    failed_images: number
    skipped_images: number
    conversion_time: number
  }
}

export interface ConversionRequest {
  markdown: string
  quality?: number
  use_image_bed?: boolean
  image_bed_provider?: string
  image_bed_config?: Record<string, any>
}

export interface HealthStatus {
  status: string
  conversion_available: boolean
  upload_available: boolean
}

export interface ImageBedConfig {
  type: string
  provider: string
  enabled: boolean
  config: Record<string, any>
}

export interface WebSocketManager {
  // WebSocket管理器接口（如果需要的话）
}

// API 服务类
export class MeowdownAPI {
  private static async httpGet<T>(path: string): Promise<T> {
    const url = `${getApiBaseUrl()}${path}`
    
    try {
      let response: string
      
      // 优先使用Tauri命令（如果可用）
      if (tauriInvoke) {
        response = await tauriInvoke('http_get', { url })
      } else {
        // 回退到原生fetch
        const fetchResponse = await fetch(url)
        if (!fetchResponse.ok) {
          throw new Error(`HTTP ${fetchResponse.status}: ${fetchResponse.statusText}`)
        }
        response = await fetchResponse.text()
      }
      
      return JSON.parse(response) as T
    } catch (e) {
      console.error('HTTP GET 请求失败:', e)
      throw e
    }
  }

  private static async httpPost<T>(path: string, body: any): Promise<T> {
    const url = `${getApiBaseUrl()}${path}`
    
    try {
      let response: string
      const bodyStr = JSON.stringify(body)
      
      // 优先使用Tauri命令（如果可用）
      if (tauriInvoke) {
        response = await tauriInvoke('http_post', { url, body: bodyStr })
      } else {
        // 回退到原生fetch
        const fetchResponse = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: bodyStr
        })
        
        if (!fetchResponse.ok) {
          throw new Error(`HTTP ${fetchResponse.status}: ${fetchResponse.statusText}`)
        }
        response = await fetchResponse.text()
      }
      
      return JSON.parse(response) as T
    } catch (e) {
      console.error('HTTP POST 请求失败:', e)
      throw e
    }
  }

  // 健康检查
  static async healthCheck(): Promise<HealthStatus> {
    return await this.httpGet<HealthStatus>('/health')
  }

  // 转换 Markdown
  static async convertMarkdown(request: ConversionRequest): Promise<ConversionResponse> {
    return await this.httpPost<ConversionResponse>('/api/convert', request)
  }

  // 上传文件
  static async uploadFile(_file: File): Promise<{ url: string }> {
    // 注意：文件上传可能需要特殊处理，暂时保留这个接口
    throw new Error('文件上传功能待实现')
  }

  // 测试图床配置
  static async testImageBedConfig(config: Record<string, any>): Promise<{ success: boolean }> {
    return await this.httpPost<{ success: boolean }>('/api/imagebed/test', config)
  }

  // 获取图床配置
  static async getImageBedConfig(): Promise<Record<string, any>> {
    return await this.httpGet<Record<string, any>>('/api/imagebed/config')
  }

  // 保存图床配置
  static async saveImageBedConfig(config: Record<string, any>): Promise<{ success: boolean }> {
    return await this.httpPost<{ success: boolean }>('/api/imagebed/config', config)
  }
}