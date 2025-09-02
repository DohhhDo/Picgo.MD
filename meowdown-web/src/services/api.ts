// 使用 Rust 命令进行HTTP请求
import { invoke } from '@tauri-apps/api/core'
import { getApiBaseUrl } from './config'

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
      const response = await invoke('http_get', { url })
      return JSON.parse(response as string) as T
    } catch (e) {
      console.error('HTTP GET 请求失败:', e)
      throw e
    }
  }

  private static async httpPost<T>(path: string, body: any): Promise<T> {
    const url = `${getApiBaseUrl()}${path}`
    
    try {
      const response = await invoke('http_post', { 
        url, 
        body: JSON.stringify(body) 
      })
      
      return JSON.parse(response as string) as T
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
    return await this.httpPost<ConversionResponse>('/convert', request)
  }

  // 上传文件
  static async uploadFile(_file: File): Promise<{ url: string }> {
    // 注意：文件上传可能需要特殊处理，暂时保留这个接口
    throw new Error('文件上传功能待实现')
  }

  // 测试图床配置
  static async testImageBedConfig(config: Record<string, any>): Promise<{ success: boolean }> {
    return await this.httpPost<{ success: boolean }>('/image-bed/test', config)
  }

  // 获取图床配置
  static async getImageBedConfig(): Promise<Record<string, any>> {
    return await this.httpGet<Record<string, any>>('/image-bed/config')
  }

  // 保存图床配置
  static async saveImageBedConfig(config: Record<string, any>): Promise<{ success: boolean }> {
    return await this.httpPost<{ success: boolean }>('/image-bed/config', config)
  }
}